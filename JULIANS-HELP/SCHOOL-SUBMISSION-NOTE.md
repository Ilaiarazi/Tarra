# School submission note

For Ilai's reference. Claude doesn't need to act on this.

This branch (`julians-initialize`) added some one-time scaffolding to help migrate Tarra from Replit to Claude Code. Once onboarding finishes:

- The `JULIANS-HELP/` folder is gone.
- The starter `CLAUDE.md` is replaced with a real one.
- The branch is ready to merge into `main`.

After the merge, the project state is clean — no trace of the scaffolding in the working tree.

If your teacher will look at the git **history** (commits, not just files):

- The scaffolding shows up across a handful of commits with messages like "Add JULIANS-HELP/..." and a final "Onboarding complete — graduate to real CLAUDE.md."
- If that's weird for your submission, you can squash the whole branch into one commit before merging:
  ```
  git checkout julians-initialize
  git reset --soft main
  git commit -m "Project setup"
  ```
- Or just delete the branch's history entirely after merging:
  ```
  git branch -d julians-initialize
  ```

If your teacher only looks at the final code (most common), you don't need to do anything.
