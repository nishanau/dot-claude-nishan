# /bootstrap — Environment Verification

Probe the current project environment and verify everything needed to develop, build, and test is working. Fix gaps. Report results.

## Steps

1. **Detect project type** by checking for:
   - `package.json` / `tsconfig.json` → Node/TypeScript project
   - `pyproject.toml` / `setup.py` / `manage.py` → Python project
   - `app.json` / `expo` in package.json → Expo/React Native project
   - `Makefile` → Has make targets
   - Multiple of the above → Monorepo

2. **Verify tooling** for detected project type:
   - Node: npm/pnpm installed, correct version, node_modules exists and is clean
   - Python: uv installed, venv exists, dependencies synced
   - Expo: ANDROID_HOME set, local.properties exists at correct location
   - General: git, make (if Makefile exists)

3. **Verify configuration**:
   - .env or .env.local exists (don't read contents, just confirm presence)
   - tsconfig.json valid (if TS project)
   - Working directory is correct (not a parent or sibling)

4. **Verify ports** (if dev server project):
   - Check that the expected dev port is not in use
   - Avoid Windows-reserved ports (8090, etc.)

5. **Test the build/dev server**:
   - Run the build or dev server briefly to confirm it starts
   - Run the test suite to confirm it passes

6. **Report a checklist**:
   ```
   [x] Project type: <detected>
   [x] Node v22.x — npm v10.x
   [x] Dependencies installed
   [x] .env present
   [x] TypeScript compiles clean
   [x] Tests pass (14/14)
   [ ] ISSUE: Port 3000 in use by PID 1234
   ```

Fix any issues found automatically where safe. For destructive fixes (deleting node_modules, etc.), ask first.
