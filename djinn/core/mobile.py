"""
Mobile & Frontend - React, Flutter, Android, iOS.
"""
from typing import Optional


class ReactPlugin:
    """React/Next.js command generator."""
    
    SYSTEM_PROMPT = """You are a React expert. Generate React/Next.js commands.

Examples:
- "create app" -> npx create-next-app my-app
- "add component" -> npx shadcn-ui add button
- "dev server" -> npm run dev
- "build" -> npm run build"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class FlutterPlugin:
    """Flutter/Dart command generator."""
    
    SYSTEM_PROMPT = """You are a Flutter expert. Generate Flutter commands.

Examples:
- "create project" -> flutter create my_app
- "run" -> flutter run
- "build apk" -> flutter build apk
- "add package" -> flutter pub add package_name"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class AndroidPlugin:
    """Android/ADB command generator."""
    
    SYSTEM_PROMPT = """You are an Android/ADB expert. Generate ADB commands.

Examples:
- "list devices" -> adb devices
- "install apk" -> adb install app.apk
- "logcat" -> adb logcat
- "screenshot" -> adb exec-out screencap -p > screen.png"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class IOSPlugin:
    """iOS/Xcode command generator."""
    
    SYSTEM_PROMPT = """You are an iOS/Xcode expert. Generate iOS development commands.

Examples:
- "build" -> xcodebuild -project App.xcodeproj
- "run simulator" -> xcrun simctl boot "iPhone 14"
- "list simulators" -> xcrun simctl list devices
- "install pods" -> pod install"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)
