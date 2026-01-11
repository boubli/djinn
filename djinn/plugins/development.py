"""
Development Plugins - Development and programming tool commands.
"""


class NodePlugin:
    """Node.js commands."""
    
    TEMPLATES = {
        # NPM
        "npm_init": "npm init -y",
        "npm_install": "npm install",
        "npm_install_pkg": "npm install {package}",
        "npm_install_dev": "npm install -D {package}",
        "npm_install_global": "npm install -g {package}",
        "npm_uninstall": "npm uninstall {package}",
        "npm_update": "npm update",
        "npm_outdated": "npm outdated",
        "npm_audit": "npm audit",
        "npm_audit_fix": "npm audit fix",
        "npm_run": "npm run {script}",
        "npm_start": "npm start",
        "npm_test": "npm test",
        "npm_build": "npm run build",
        "npm_publish": "npm publish",
        "npm_version": "npm version {type}",
        "npm_list": "npm list --depth=0",
        "npm_cache_clean": "npm cache clean --force",
        
        # pnpm
        "pnpm_install": "pnpm install",
        "pnpm_add": "pnpm add {package}",
        "pnpm_run": "pnpm run {script}",
        
        # Yarn
        "yarn_install": "yarn install",
        "yarn_add": "yarn add {package}",
        "yarn_add_dev": "yarn add -D {package}",
        "yarn_run": "yarn {script}",
        "yarn_upgrade": "yarn upgrade",
        
        # Bun
        "bun_install": "bun install",
        "bun_add": "bun add {package}",
        "bun_run": "bun run {script}",
        
        # Node
        "node_run": "node {file}",
        "node_inspect": "node --inspect {file}",
        "node_version": "node --version",
    }


class PythonPlugin:
    """Python development commands."""
    
    TEMPLATES = {
        # Virtual environments
        "venv_create": "python -m venv venv",
        "venv_activate_unix": "source venv/bin/activate",
        "venv_activate_win": "venv\\Scripts\\activate",
        "venv_deactivate": "deactivate",
        
        # Pip
        "pip_install": "pip install {package}",
        "pip_install_req": "pip install -r requirements.txt",
        "pip_freeze": "pip freeze > requirements.txt",
        "pip_list": "pip list",
        "pip_outdated": "pip list --outdated",
        "pip_upgrade": "pip install --upgrade {package}",
        "pip_uninstall": "pip uninstall {package}",
        "pip_show": "pip show {package}",
        
        # Poetry
        "poetry_init": "poetry init",
        "poetry_install": "poetry install",
        "poetry_add": "poetry add {package}",
        "poetry_add_dev": "poetry add -D {package}",
        "poetry_run": "poetry run {command}",
        "poetry_shell": "poetry shell",
        "poetry_build": "poetry build",
        "poetry_publish": "poetry publish",
        
        # UV (fast pip)
        "uv_install": "uv pip install {package}",
        "uv_sync": "uv pip sync requirements.txt",
        "uv_compile": "uv pip compile requirements.in -o requirements.txt",
        
        # Testing
        "pytest": "pytest",
        "pytest_verbose": "pytest -v",
        "pytest_coverage": "pytest --cov={package}",
        "pytest_watch": "pytest-watch",
        "unittest": "python -m unittest discover",
        
        # Linting/Formatting
        "black": "black .",
        "ruff": "ruff check .",
        "ruff_fix": "ruff check --fix .",
        "mypy": "mypy .",
        "flake8": "flake8 .",
        "isort": "isort .",
        "pylint": "pylint {module}",
        
        # Run
        "python_run": "python {file}",
        "python_module": "python -m {module}",
        "python_interactive": "python -i {file}",
        
        # Build
        "build": "python -m build",
        "twine_upload": "twine upload dist/*",
    }


class GoPlugin:
    """Go development commands."""
    
    TEMPLATES = {
        "mod_init": "go mod init {module}",
        "mod_tidy": "go mod tidy",
        "mod_download": "go mod download",
        "build": "go build",
        "build_output": "go build -o {output}",
        "run": "go run .",
        "run_file": "go run {file}",
        "test": "go test ./...",
        "test_verbose": "go test -v ./...",
        "test_cover": "go test -cover ./...",
        "fmt": "go fmt ./...",
        "vet": "go vet ./...",
        "lint": "golangci-lint run",
        "get": "go get {package}",
        "install": "go install",
        "version": "go version",
    }


class RustPlugin:
    """Rust development commands."""
    
    TEMPLATES = {
        "new": "cargo new {name}",
        "new_lib": "cargo new --lib {name}",
        "build": "cargo build",
        "build_release": "cargo build --release",
        "run": "cargo run",
        "test": "cargo test",
        "check": "cargo check",
        "fmt": "cargo fmt",
        "clippy": "cargo clippy",
        "add": "cargo add {package}",
        "update": "cargo update",
        "doc": "cargo doc --open",
        "publish": "cargo publish",
    }


class JavaPlugin:
    """Java development commands."""
    
    TEMPLATES = {
        # Maven
        "mvn_compile": "mvn compile",
        "mvn_test": "mvn test",
        "mvn_package": "mvn package",
        "mvn_install": "mvn install",
        "mvn_clean": "mvn clean",
        "mvn_run": "mvn exec:java",
        "mvn_dependency": "mvn dependency:tree",
        
        # Gradle
        "gradle_build": "gradle build",
        "gradle_test": "gradle test",
        "gradle_run": "gradle run",
        "gradle_clean": "gradle clean",
        "gradle_tasks": "gradle tasks",
    }


class DotNetPlugin:
    """.NET development commands."""
    
    TEMPLATES = {
        "new": "dotnet new {template}",
        "build": "dotnet build",
        "run": "dotnet run",
        "test": "dotnet test",
        "publish": "dotnet publish -c Release",
        "restore": "dotnet restore",
        "add_package": "dotnet add package {package}",
        "ef_migrate": "dotnet ef migrations add {name}",
        "ef_update": "dotnet ef database update",
    }


class RubyPlugin:
    """Ruby development commands."""
    
    TEMPLATES = {
        "bundle_install": "bundle install",
        "bundle_exec": "bundle exec {command}",
        "gem_install": "gem install {gem}",
        "rails_new": "rails new {name}",
        "rails_server": "rails server",
        "rails_console": "rails console",
        "rails_migrate": "rails db:migrate",
        "rails_routes": "rails routes",
        "rspec": "rspec",
        "rubocop": "rubocop",
    }


class PHPPlugin:
    """PHP development commands."""
    
    TEMPLATES = {
        "composer_install": "composer install",
        "composer_require": "composer require {package}",
        "composer_update": "composer update",
        "composer_dump": "composer dump-autoload",
        "artisan": "php artisan {command}",
        "artisan_serve": "php artisan serve",
        "artisan_migrate": "php artisan migrate",
        "artisan_tinker": "php artisan tinker",
        "phpunit": "vendor/bin/phpunit",
        "php_lint": "php -l {file}",
    }


class FlutterPlugin:
    """Flutter development commands."""
    
    TEMPLATES = {
        "create": "flutter create {name}",
        "run": "flutter run",
        "build_apk": "flutter build apk",
        "build_ios": "flutter build ios",
        "build_web": "flutter build web",
        "test": "flutter test",
        "pub_get": "flutter pub get",
        "pub_add": "flutter pub add {package}",
        "doctor": "flutter doctor",
        "clean": "flutter clean",
    }


class TerraformPlugin:
    """Terraform IaC commands."""
    
    TEMPLATES = {
        "init": "terraform init",
        "plan": "terraform plan",
        "apply": "terraform apply",
        "apply_auto": "terraform apply -auto-approve",
        "destroy": "terraform destroy",
        "validate": "terraform validate",
        "fmt": "terraform fmt",
        "output": "terraform output",
        "state_list": "terraform state list",
        "state_show": "terraform state show {resource}",
        "import": "terraform import {resource} {id}",
        "workspace_list": "terraform workspace list",
        "workspace_new": "terraform workspace new {name}",
        "workspace_select": "terraform workspace select {name}",
    }


class AnsiblePlugin:
    """Ansible automation commands."""
    
    TEMPLATES = {
        "playbook": "ansible-playbook {playbook}.yml",
        "playbook_check": "ansible-playbook {playbook}.yml --check",
        "playbook_verbose": "ansible-playbook {playbook}.yml -vvv",
        "inventory": "ansible-inventory --list",
        "ping": "ansible all -m ping",
        "command": "ansible all -m command -a '{command}'",
        "galaxy_install": "ansible-galaxy install {role}",
        "vault_create": "ansible-vault create {file}",
        "vault_edit": "ansible-vault edit {file}",
        "vault_encrypt": "ansible-vault encrypt {file}",
        "vault_decrypt": "ansible-vault decrypt {file}",
    }
