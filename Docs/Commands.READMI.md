# 📚 GitHub Commands Guide

> New to Git and GitHub? Start here!

## 🎯 What is Git?

Think of Git as a "save game" system for code. It tracks every change, lets you go back in time, and helps teams work together without breaking things.

---

## 🚀 Essential Commands

### Start Working
```bash
# Download the project to your computer
git clone <main-repository-url>

# Go into the project folder
cd Ai-Powered-Resume-Filtering-and-Ranking
```

### Daily Work
```bash
# Check what files you changed
git status

# Check which branch you're on
git branch

# Switch to your branch (if not already on it)
git checkout Your-branch-name

# Save your changes
git add .
git commit -m "describe what you did"

# Upload your work to GitHub
git push origin Your-branch-name
```

### Get Latest Updates
```bash
# Switch to main branch
git checkout main

# Download latest changes from main
git pull origin main

# Switch back to your branch
git checkout Your-branch-name

# Merge latest main changes into your branch (optional but recommended)
git merge main
```

---

## 🔄 Creating a Pull Request (PR)

### What is a Pull Request?

A **Pull Request** is how you ask to merge your code into the main branch. Think of it as saying: *"Hey team, I finished my work. Can you review it and add it to the main project?"*

### Step-by-Step: Creating Your First PR

#### Step 1: Make Sure Your Code is Pushed
```bash
# Check your status
git status

# If you have changes, save them
git add .
git commit -m "completed feature X"

# Push to your branch
git push origin Your-branch-name
```

#### Step 2: Go to GitHub Website

1. Open your browser and go to: `https://github.com/your-repo-name`
2. You'll see a yellow banner saying: **"Your-branch-name had recent pushes"**
3. Click the green button: **"Compare & pull request"**

#### Step 3: Fill Out the PR Form

**Title:** Write a clear title
```
Good: "Added PDF parsing functionality"
Bad: "updated code"
```

**Description:** Explain what you did
```
## What I Built
- Added PDF parser using PyPDF2
- Handles multi-page resumes
- Tested with 20 sample files

## Testing
- All tests passing ✓
- No errors on different PDF formats

## Ready for Review
@Mahesh please review when you have time
```

#### Step 4: Create the Pull Request

1. Make sure **base branch** is `main`
2. Make sure **compare branch** is `Your-branch-name`
3. Click **"Create Pull Request"**

### PR Review Process

```
You → Create PR → Team Reviews → Approve → Mahesh Merges → Your code in main! 🎉
```

**What happens next:**

1. **Team gets notified** - They'll see your PR
2. **Code review** - Others will check your code
3. **Comments/Feedback** - They might suggest changes
4. **You update** - Make requested changes if needed
5. **Approval** - Once approved, Mahesh merges it
6. **Merged!** - Your code is now in the main project

---

## 🌿 Branch Strategy

```
main (protected - only Mahesh can merge)
  ├── Resume-Parsing-Vaishnavi         (Parser team)
  ├── NLP-and-Skill-extraction-Mahesh  (NLP team)
  ├── AI-Matching-and-Scoring-Yograj   (Scoring team)
  ├── Backend-Mayur                    (Backend team)
  └── Frontend-pavan                   (Frontend team)
```

**Rule:** Never work directly on `main`. Always work on your own branch!

---

## ✅ Complete Workflow Example

### Day 1: Starting Your Work
```bash
# Get latest code
git checkout main
git pull origin main

# Create/switch to your branch
git checkout Your-branch-name

# Start coding... ⌨️
```

### Day 2: Save Progress
```bash
# Check what you changed
git status

# Save your work
git add .
git commit -m "added skill extraction logic"

# Upload to GitHub
git push origin Your-branch-name
```

### Day 3: Feature Complete - Create PR
```bash
# Final commit
git add .
git commit -m "completed skill extraction module with tests"
git push origin Your-branch-name

# Now go to GitHub website and create Pull Request
```

### After PR is Merged
```bash
# Update your local main branch
git checkout main
git pull origin main

# Your code is now in main! 🎉
# Start next feature on a new branch if needed
```

---

## 🎯 Best Practices

### Before You Start Working
1. ✅ **Always pull latest main** - `git pull origin main`
2. ✅ **Work on your branch** - Never on main directly
3. ✅ **Check which branch you're on** - `git branch`

### While Working
1. ✅ **Commit often** - Save progress regularly
2. ✅ **Write clear messages** - "Added PDF parser" not "updated stuff"
3. ✅ **Test your code** - Make sure it works before pushing

### Before Creating PR
1. ✅ **Pull latest main** - Make sure you have latest changes
2. ✅ **Merge main into your branch** - Avoid conflicts
3. ✅ **Test everything** - Make sure nothing broke
4. ✅ **Write good PR description** - Help reviewers understand

### After PR is Created
1. ✅ **Respond to feedback** - Answer questions quickly
2. ✅ **Make requested changes** - Update your code if needed
3. ✅ **Be patient** - Reviews take time
4. ✅ **Learn from feedback** - Improve for next time

---

## 🆘 Common Problems & Solutions

### Problem 1: "I'm on the wrong branch!"
```bash
# Save your work first
git stash

# Switch to correct branch
git checkout Your-branch-name

# Get your work back
git stash pop
```

### Problem 2: "I messed up, help!"
```bash
# Undo uncommitted changes
git checkout .

# Go back to last commit (WARNING: loses all changes)
git reset --hard HEAD
```

### Problem 3: "My branch is outdated"
```bash
# Get latest main
git checkout main
git pull origin main

# Update your branch
git checkout Your-branch-name
git merge main

# If conflicts appear, ask for help!
```

### Problem 4: "Merge Conflicts!"
```bash
# Don't panic! This is normal.
# Open the conflicting files
# Look for <<<<<<< and >>>>>>>
# Choose which code to keep
# Remove the conflict markers
# Then:

git add .
git commit -m "resolved merge conflicts"
git push origin Your-branch-name
```

### Problem 5: "I committed to main by mistake!"
```bash
# STOP! Don't push!
# Ask Mahesh for help immediately
# This needs careful fixing
```

---

## 📋 PR Review Checklist

### Before Creating PR:
- [ ] Code works and tested
- [ ] No errors in console/terminal
- [ ] Followed coding standards
- [ ] Added comments for complex parts
- [ ] Updated documentation if needed
- [ ] Branch is up to date with main

### PR Description Should Include:
- [ ] What you built
- [ ] How to test it
- [ ] Screenshots (if UI changes)
- [ ] Any questions for reviewers

---

## 💬 Good Commit Message Examples

✅ **Good:**
```bash
git commit -m "add PDF parsing with PyPDF2 library"
git commit -m "fix: handle corrupted PDF files gracefully"
git commit -m "improve skill extraction accuracy by 15%"
git commit -m "add unit tests for resume parser"
```

❌ **Bad:**
```bash
git commit -m "update"
git commit -m "changes"
git commit -m "fixed stuff"
git commit -m "asdfgh"
```

---

## 🎓 Why This Matters

### For Your Learning
- ✅ Track every change (never lose work)
- ✅ Work together without conflicts
- ✅ Review each other's code
- ✅ Professional development practice
- ✅ Portfolio-ready workflow

### For Your Career
- 💼 **All companies use Git/GitHub**
- 📈 **Shows teamwork skills**
- 🏆 **Demonstrates code quality**
- 📝 **Proves communication ability**
- 🎯 **Real project experience**

---

## 🚀 Quick Reference Card

### Most Used Commands:
```bash
git status              # What changed?
git add .               # Save all changes
git commit -m "msg"     # Commit with message
git push origin branch  # Upload to GitHub
git pull origin main    # Get latest main
git checkout branch     # Switch branches
git branch              # Which branch am I on?
```

### Daily Routine:
```bash
1. git checkout main
2. git pull origin main
3. git checkout Your-branch-name
4. # Do your work
5. git add .
6. git commit -m "what you did"
7. git push origin Your-branch-name
```

---

## 📞 Getting Help

### When Stuck:
1. **Google it** - "git how to..." usually works
2. **Ask your team** - We're here to help!
3. **Check GitHub docs** - Great tutorials
4. **Ask Mahesh** - Project lead knows best


---

## 🎯 Team Guidelines

### PR Review Time
- **Create PR:** Anytime after feature is complete
- **Review Time:** Within 24 hours
- **Merge:** Mahesh merges after approval

### Communication
- 💬 Comment on PRs with questions
- 📝 Be respectful and helpful in reviews
- 🤝 Everyone's learning together

### Code Quality
- Write clean, readable code
- Add comments for tricky parts
- Test before creating PR
- Ask for help if unsure

---

<div align="center">

## 🌟 Remember

**Git is a tool, not a test.**  
**Everyone makes mistakes.**  
**Ask questions early and often.**  
**We succeed together!**

---

**Still confused?** Ask your team lead - everyone was new once!


</div>