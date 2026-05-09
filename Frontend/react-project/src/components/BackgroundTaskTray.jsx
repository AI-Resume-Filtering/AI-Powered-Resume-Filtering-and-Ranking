import { useMemo } from "react";
import { useBackgroundTasks } from "../context/BackgroundTasksContext";
import "../styles/BackgroundTaskTray.css";

function BackgroundTaskTray() {
  const { tasks, clearTask } = useBackgroundTasks();

  const visibleTasks = useMemo(() => tasks.slice(0, 5), [tasks]);
  const hasTasks = visibleTasks.length > 0;

  if (!hasTasks) return null;

  return (
    <div className="bgt-tray" aria-live="polite">
      <h4 className="bgt-title">Background Tasks</h4>
      {visibleTasks.map((task) => (
        <div key={task.id} className={`bgt-item bgt-${task.state}`}>
          <div className="bgt-item-head">
            <strong>{task.title}</strong>
            {task.state !== "running" ? (
              <button className="bgt-close" onClick={() => clearTask(task.id)}>
                x
              </button>
            ) : null}
          </div>
          <p className="bgt-message">{task.message}</p>
        </div>
      ))}
    </div>
  );
}

export default BackgroundTaskTray;
