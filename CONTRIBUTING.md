Hey Guys! 
Please follow these guidelines to ensure a smooth and collaborative workflow.

## Project Set-Up
Clone the project

```sh
git clone https://github.com/nas3ts/pcrs.git
```

Follow the setup guides:
- [backend](backend/SETUP.md)
- [frontend](frontend/SETUP.md)

## Branching Strategy
- Use **`feat` branches** for new features (`feat/your-feature`).
- Use **`fix` branches** for fixes (`fix/your-fix`).<br>
**Note**: There is a `develop` branch and `main` branch.
- Merge into `develop` before `main` unless it's a hotfix (a quick software update that fixes a critical issue without a full release).

## Commit Message Format
Follow the [Conventional Commits](https://www.conventionalcommits.org/) format to ensure consistency:

- `feat:` → Adding a new feature
- `fix:` → Fixing a bug
- `chore:` → General maintenance (e.g., refactoring, dependencies)
- `docs:` → Documentation updates
- `refactor:` → Code changes that don’t add features or fix bugs
- `test:` → Adding or updating tests
- `ci:` → Changes to CI/CD workflows

**Example Commit Messages:**
```sh
feat: add user authentication
fix: resolve crash on profile page
chore: update dependencies
```

## Making Changes
- Follow the team’s **coding standards** and best practices.
- Write clear and concise **commit messages** as per the format above.
- Run tests before submitting changes:
  ```sh
  python manage.py test
  ```
- Ensure your code is reviewed by at least one team member before merging.

## Submitting a Pull Request
1. **Ensure your branch is up to date** with `develop`:
   ```sh
   git checkout develop
   git pull origin develop
   git checkout feature-branch
   git merge develop
   ```
2. **Push your changes**:
   ```sh
   git push origin feature-branch
   ```
3. **Create a Pull Request (PR)** on GitHub:
   - Assign relevant reviewers.
   - Provide a clear description of the changes.
   - Mention any issues it fixes (e.g., `Fixes #123`).
   - Wait for team feedback before merging.

## Communication
- Let's talk on the WhatsApp group.

Happy coding! 🚀

