"""
Unreal Connector - Read/Write Unreal Engine project files
Handles C++ and Blueprint class generation
"""

import os
from pathlib import Path
import json
from datetime import datetime

class UnrealConnector:
    def __init__(self, project_path):
        self.project_path = Path(project_path)
        
        # Find .uproject file
        uproject_files = list(self.project_path.glob('*.uproject'))
        if not uproject_files:
            raise ValueError(f"Not a valid Unreal project: {project_path}")
        
        self.project_file = uproject_files[0]
        self.project_name = self.project_file.stem
        
        # Standard Unreal paths
        self.source_path = self.project_path / "Source" / self.project_name
        self.content_path = self.project_path / "Content"
        
        # Create Source folder if needed
        self.source_path.mkdir(parents=True, exist_ok=True)
        
        # Action log
        self.log_file = Path('logs/unreal_actions.json')
        self.log_file.parent.mkdir(exist_ok=True)
    
    def get_project_structure(self):
        """Analyze Unreal project structure"""
        structure = {
            "project_name": self.project_name,
            "cpp_classes": [],
            "blueprints": [],
            "maps": []
        }
        
        # Scan Source folder for C++ classes
        if self.source_path.exists():
            for root, dirs, files in os.walk(self.source_path):
                rel_path = Path(root).relative_to(self.source_path)
                for file in files:
                    if file.endswith('.h') or file.endswith('.cpp'):
                        structure["cpp_classes"].append(str(rel_path / file))
        
        # Scan Content folder for assets
        if self.content_path.exists():
            for root, dirs, files in os.walk(self.content_path):
                rel_path = Path(root).relative_to(self.content_path)
                for file in files:
                    if file.endswith('.uasset'):
                        if 'Blueprint' in file:
                            structure["blueprints"].append(str(rel_path / file))
                        elif 'Map' in file or file.endswith('_Level.uasset'):
                            structure["maps"].append(str(rel_path / file))
        
        return structure
    
    def create_cpp_class(self, class_name, header_content, source_content):
        """Create a new C++ class (header and source files)"""
        
        header_path = self.source_path / f"{class_name}.h"
        source_path = self.source_path / f"{class_name}.cpp"
        
        try:
            # Create header file
            if header_path.exists():
                backup = header_path.with_suffix('.h.bak')
                header_path.rename(backup)
            header_path.write_text(header_content, encoding='utf-8')
            
            # Create source file
            if source_path.exists():
                backup = source_path.with_suffix('.cpp.bak')
                source_path.rename(backup)
            source_path.write_text(source_content, encoding='utf-8')
            
            self.log_action('create', f"{class_name}.h/.cpp", "C++ class created")
            
            return {
                "success": True,
                "header": str(header_path.relative_to(self.project_path)),
                "source": str(source_path.relative_to(self.project_path)),
                "message": f"C++ class created: {class_name}"
            }
        
        except Exception as e:
            self.log_action('error', class_name, str(e))
            return {"success": False, "error": str(e)}
    
    def get_cpp_class_template(self, class_type="Actor"):
        """Get template for Unreal C++ classes"""
        
        templates = {
            "Actor": {
                "header": """// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "{ClassName}.generated.h"

UCLASS()
class {PROJECT}_API A{ClassName} : public AActor
{{
    GENERATED_BODY()
    
public:    
    // Sets default values for this actor's properties
    A{ClassName}();

protected:
    // Called when the game starts or when spawned
    virtual void BeginPlay() override;

public:    
    // Called every frame
    virtual void Tick(float DeltaTime) override;

}};
""",
                "source": """// Fill out your copyright notice in the Description page of Project Settings.

#include "{ClassName}.h"

// Sets default values
A{ClassName}::A{ClassName}()
{{
    // Set this actor to call Tick() every frame
    PrimaryActorTick.bCanEverTick = true;
}}

// Called when the game starts or when spawned
void A{ClassName}::BeginPlay()
{{
    Super::BeginPlay();
}}

// Called every frame
void A{ClassName}::Tick(float DeltaTime)
{{
    Super::Tick(DeltaTime);
}}
"""
            },
            "Character": {
                "header": """#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "{ClassName}.generated.h"

UCLASS()
class {PROJECT}_API A{ClassName} : public ACharacter
{{
    GENERATED_BODY()

public:
    A{ClassName}();

protected:
    virtual void BeginPlay() override;

public:    
    virtual void Tick(float DeltaTime) override;
    virtual void SetupPlayerInputComponent(class UInputComponent* PlayerInputComponent) override;

private:
    void MoveForward(float Value);
    void MoveRight(float Value);
}};
""",
                "source": """#include "{ClassName}.h"

A{ClassName}::A{ClassName}()
{{
    PrimaryActorTick.bCanEverTick = true;
}}

void A{ClassName}::BeginPlay()
{{
    Super::BeginPlay();
}}

void A{ClassName}::Tick(float DeltaTime)
{{
    Super::Tick(DeltaTime);
}}

void A{ClassName}::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{{
    Super::SetupPlayerInputComponent(PlayerInputComponent);
    
    PlayerInputComponent->BindAxis("MoveForward", this, &A{ClassName}::MoveForward);
    PlayerInputComponent->BindAxis("MoveRight", this, &A{ClassName}::MoveRight);
}}

void A{ClassName}::MoveForward(float Value)
{{
    if (Value != 0.0f)
    {{
        AddMovementInput(GetActorForwardVector(), Value);
    }}
}}

void A{ClassName}::MoveRight(float Value)
{{
    if (Value != 0.0f)
    {{
        AddMovementInput(GetActorRightVector(), Value);
    }}
}}
"""
            }
        }
        
        template = templates.get(class_type, templates["Actor"])
        return {
            "header": template["header"].replace("{PROJECT}", self.project_name.upper()),
            "source": template["source"]
        }
    
    def list_cpp_classes(self):
        """List all C++ classes in the project"""
        classes = []
        
        if self.source_path.exists():
            for root, dirs, files in os.walk(self.source_path):
                for file in files:
                    if file.endswith('.h'):
                        full_path = Path(root) / file
                        rel_path = full_path.relative_to(self.source_path)
                        classes.append({
                            "name": file,
                            "path": str(rel_path),
                            "size": full_path.stat().st_size,
                            "modified": datetime.fromtimestamp(
                                full_path.stat().st_mtime
                            ).strftime("%Y-%m-%d %H:%M")
                        })
        
        return classes
    
    def log_action(self, action_type, target, details):
        """Log actions"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action_type,
            "target": target,
            "details": details
        }
        
        if self.log_file.exists():
            with open(self.log_file, 'r') as f:
                logs = json.load(f)
        else:
            logs = []
        
        logs.append(log_entry)
        
        with open(self.log_file, 'w') as f:
            json.dump(logs[-500:], f, indent=2)