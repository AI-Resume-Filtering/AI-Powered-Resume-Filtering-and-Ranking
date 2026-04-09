import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from "react";
import API from "../api";

const BackgroundTasksContext = createContext(null);
const STORAGE_KEY = "background_tasks_v1";

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

function createTaskId() {
  return `task_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`;
}

export function BackgroundTasksProvider({ children }) {
  const [tasks, setTasks] = useState([]);
  const hydratedRef = useRef(false);

  const updateTask = useCallback((taskId, patch) => {
    setTasks((prev) =>
      prev.map((task) => (task.id === taskId ? { ...task, ...patch, updatedAt: Date.now() } : task))
    );
  }, []);

  const resumeTaskAfterRefresh = useCallback(
    async (task) => {
      if (!task?.resume) {
        updateTask(task.id, {
          state: "error",
          message: "Task was interrupted by page refresh and could not be resumed.",
        });
        return;
      }

      try {
        if (task.resume.kind === "application-status") {
          const applicationId = task.resume.applicationId;
          if (!applicationId) {
            throw new Error("Missing application id for status resume.");
          }

          updateTask(task.id, { message: "Resuming application status check..." });

          for (;;) {
            const result = await API.getApplicationStatus(applicationId);
            if (result?.status === "processing") {
              await sleep(3000);
              continue;
            }
            if (result?.status === "error") {
              throw new Error("Resume processing failed. Please try again.");
            }

            updateTask(task.id, {
              state: "success",
              message: task.resume.successMessage || "Application processing completed.",
              resume: null,
            });
            return;
          }
        }

        if (task.resume.kind === "api-call") {
          const { action, payload, successMessage } = task.resume;
          updateTask(task.id, { message: "Resuming task after refresh..." });

          let data = null;
          if (action === "deleteJob") {
            data = await API.deleteJob(payload?.jobId);
          } else if (action === "saveEmailTemplate") {
            data = await API.saveEmailTemplate(
              payload?.companyId,
              payload?.subject,
              payload?.body
            );
          } else if (action === "saveCompanyScoreThreshold") {
            data = await API.saveCompanyScoreThreshold(
              payload?.companyId,
              payload?.scoreThreshold
            );
          } else {
            throw new Error("Unknown resumable task type.");
          }

          if (!data?.success) {
            throw new Error(data?.message || "Task could not be resumed.");
          }

          updateTask(task.id, {
            state: "success",
            message: successMessage || "Completed",
            resume: null,
          });
          return;
        }

        throw new Error("Unsupported resumable task.");
      } catch (error) {
        updateTask(task.id, {
          state: "error",
          message: error?.message || "Task resume failed after refresh.",
          resume: null,
        });
      }
    },
    [updateTask]
  );

  const runTask = useCallback((meta, worker) => {
    const taskId = createTaskId();
    const now = Date.now();
    const task = {
      id: taskId,
      title: meta?.title || "Background task",
      type: meta?.type || "generic",
      state: "running",
      message: meta?.message || "Processing...",
      resume: meta?.resume || null,
      createdAt: now,
      updatedAt: now,
    };

    setTasks((prev) => [task, ...prev]);

    const promise = (async () => {
      try {
        const result = await worker({
          taskId,
          update: (patch) => updateTask(taskId, patch),
          sleep,
        });

        updateTask(taskId, {
          state: "success",
          message: "Completed",
          resume: null,
        });

        return result;
      } catch (error) {
        updateTask(taskId, {
          state: "error",
          message: error?.message || "Task failed",
          resume: null,
        });
        throw error;
      }
    })();

    return { taskId, promise };
  }, [updateTask]);

  const clearTask = useCallback((taskId) => {
    setTasks((prev) => prev.filter((task) => task.id !== taskId));
  }, []);

  useEffect(() => {
    if (hydratedRef.current) return;
    hydratedRef.current = true;

    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return;

      const persisted = JSON.parse(raw);
      if (!Array.isArray(persisted) || persisted.length === 0) return;

      setTasks(persisted);

      persisted
        .filter((task) => task?.state === "running")
        .forEach((task) => {
          void resumeTaskAfterRefresh(task);
        });
    } catch {
      localStorage.removeItem(STORAGE_KEY);
    }
  }, [resumeTaskAfterRefresh]);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks.slice(0, 30)));
    } catch {
      // Ignore storage quota / privacy mode failures.
    }
  }, [tasks]);

  const value = useMemo(
    () => ({
      tasks,
      runTask,
      updateTask,
      clearTask,
    }),
    [tasks, runTask, updateTask, clearTask]
  );

  return (
    <BackgroundTasksContext.Provider value={value}>
      {children}
    </BackgroundTasksContext.Provider>
  );
}

export function useBackgroundTasks() {
  const ctx = useContext(BackgroundTasksContext);
  if (!ctx) {
    throw new Error("useBackgroundTasks must be used inside BackgroundTasksProvider");
  }
  return ctx;
}
