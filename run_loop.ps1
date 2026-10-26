# Execution Loop Wrapper — PowerShell
# Usage: .\run_loop.ps1 [-Run 1|2] [-Rules "loop_rules.md"]

param(
    [int]$Run = 1,
    [string]$RulesFile = ""
)

$ErrorActionPreference = "Stop"

$tasksFile = "tasks.json"
$metricsFile = "metrics.json"
$maxConsecutiveFailures = 3
$maxSameTaskFailures = 2
$projectDir = $PSScriptRoot

Write-Host "=== EXECUTION LOOP WRAPPER ===" -ForegroundColor Cyan
Write-Host "Run: $Run" -ForegroundColor Yellow
Write-Host "Project: $projectDir" -ForegroundColor Yellow
if ($RulesFile) {
    Write-Host "Rules: $RulesFile" -ForegroundColor Yellow
}
Write-Host ""

# Load tasks
$tasksJson = Get-Content $tasksFile -Raw | ConvertFrom-Json
$tasks = $tasksJson.tasks

# Load or create metrics
if (Test-Path $metricsFile) {
    $metricsJson = Get-Content $metricsFile -Raw | ConvertFrom-Json
} else {
    $metricsJson = [PSCustomObject]@{
        run = $Run
        start_time = $null
        end_time = $null
        total_tasks = $tasks.Count
        tasks_completed = 0
        tasks_failed = 0
        first_attempt_success = 0
        total_time_seconds = 0
        failed_at = $null
        failure_reason = $null
        consecutive_failures = 0
        task_results = @()
    }
}

$metricsJson.run = $Run
$metricsJson.start_time = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"

# Load rules if provided
$rulesContent = ""
if ($RulesFile -and (Test-Path $RulesFile)) {
    $rulesContent = Get-Content $RulesFile -Raw
    Write-Host "Loaded rules from $RulesFile" -ForegroundColor Green
}

$completed = 0
$failed = 0
$firstSuccess = 0
$totalTime = 0
$consecutiveFailures = 0
$taskFailures = @{}

function Update-Metrics {
    $metricsJson.tasks_completed = $completed
    $metricsJson.tasks_failed = $failed
    $metricsJson.first_attempt_success = $firstSuccess
    $metricsJson.total_time_seconds = $totalTime
    $metricsJson.consecutive_failures = $consecutiveFailures
    if ($failed -gt 0 -and -not $metricsJson.failed_at) {
        $metricsJson.failed_at = $lastFailedTask
    }
    $metricsJson | ConvertTo-Json -Depth 10 | Set-Content $metricsFile
}

function Validate-Task {
    param([string]$TaskId)
    
    Write-Host "  Validating..." -ForegroundColor Gray
    
    # Check Python can import taskmanager
    $importResult = python -c "import sys; sys.path.insert(0, '.'); import taskmanager; print('IMPORT_OK')" 2>&1
    if ($LASTEXITCODE -ne 0 -and $importResult -notmatch "IMPORT_OK") {
        Write-Host "  FAIL: Cannot import taskmanager" -ForegroundColor Red
        return $false, $importResult
    }
    
    # Run pytest if tests exist
    $testFiles = Get-ChildItem "tests\*.py" -File
    if ($testFiles.Count -gt 0) {
        $testResult = python -m pytest --tb=short -q 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "  FAIL: Tests failed" -ForegroundColor Red
            return $false, $testResult
        }
    }
    
    Write-Host "  PASS" -ForegroundColor Green
    return $true, "OK"
}

function Generate-Prompt {
    param([object]$Task, [string]$Rules)
    
    $prompt = @"
EXECUTION LOOP — Task $TaskId of $($tasks.Count)
Run: $Run
Type: $($Task.type)
Title: $($Task.title)
Acceptance criteria: $($Task.acceptance)
Files to modify: $($Task.files -join ", ")

Instructions:
1. Read the files mentioned in 'files' to understand context
2. Implement the change described in the task
3. After implementing, run: python -c "import sys; sys.path.insert(0, '.'); import taskmanager" — must succeed
4. If tests exist (tests/*.py), run: python -m pytest --tb=short — must pass
5. Commit with message: task($TaskId): $($Task.title)
6. Report: done / failed + reason

Rules:
$Rules
"@
    return $prompt
}

Write-Host "Total tasks: $($tasks.Count)" -ForegroundColor Cyan
Write-Host ""

$startTime = Get-Date
$lastFailedTask = $null

for ($i = 0; $i -lt $tasks.Count; $i++) {
    $task = $tasks[$i]
    $taskId = $task.id
    
    if ($task.status -ne "pending") {
        Write-Host "SKIP: $taskId already $($task.status)" -ForegroundColor Gray
        continue
    }
    
    Write-Host ""
    Write-Host "=== TASK $($i+1)/$($tasks.Count): $taskId ===" -ForegroundColor Cyan
    Write-Host "Type: $($task.type) | Title: $($task.title)" -ForegroundColor Yellow
    Write-Host "Acceptance: $($task.acceptance)" -ForegroundColor Gray
    
    $taskStart = Get-Date
    $taskFailures[$taskId] = 0
    $attempts = 0
    $maxAttempts = 3
    $taskDone = $false
    
    while ($attempts -lt $maxAttempts -and -not $taskDone) {
        $attempts++
        Write-Host "  Attempt $attempts/$maxAttempts..." -ForegroundColor Gray
        
        # Generate prompt for this task
        $prompt = Generate-Prompt $task $rulesContent
        
        # The prompt is printed here. In a real execution loop,
        # this would be fed to an AI assistant.
        # For now, we simulate by outputting the prompt for manual/automated processing.
        Write-Host ""
        Write-Host "--- PROMPT ---" -ForegroundColor Magenta
        Write-Host $prompt
        Write-Host "--- END PROMPT ---" -ForegroundColor Magenta
        Write-Host ""
        
        # In a real scenario, the assistant would process the prompt here.
        # For this experiment, we'll wait for the assistant to make changes,
        # then validate.
        
        # Check if changes were made (git status)
        $gitStatus = git status --porcelain 2>&1
        if (-not $gitStatus) {
            Write-Host "  No changes detected. Waiting for assistant to process..." -ForegroundColor Yellow
            # In automated mode, this would be handled by the assistant's commit
        }
        
        # Validate
        $valid, $output = Validate-Task $taskId
        if ($valid) {
            Write-Host "  Task $taskId PASSED validation!" -ForegroundColor Green
            
            # Commit
            git add -A
            git commit -m "task($taskId): $($task.title)" 2>&1 | Out-Null
            if ($LASTEXITCODE -eq 0) {
                $task.status = "done"
                $completed++
                $firstSuccess++
                $taskDone = $true
                $consecutiveFailures = 0
                $taskTime = (Get-Date) - $taskStart
                $totalTime += $taskTime.TotalSeconds
                Write-Host "  Committed. Time: $([math]::Round($taskTime.TotalSeconds, 1))s" -ForegroundColor Green
            }
        } else {
            Write-Host "  Task $taskId FAILED validation." -ForegroundColor Red
            $taskFailures[$taskId]++
            $consecutiveFailures++
            
            if ($taskFailures[$taskId] -ge $maxSameTaskFailures) {
                Write-Host "  Task $taskId failed $maxSameTaskFailures times — giving up." -ForegroundColor Red
                $task.status = "failed"
                $failed++
                $metricsJson.failed_at = $taskId
                $metricsJson.failure_reason = "Same task failed $maxSameTaskFailures times"
                $taskDone = $true
            }
        }
        
        Update-Metrics
    }
    
    if (-not $taskDone) {
        $task.status = "failed"
        $failed++
        $metricsJson.failed_at = $taskId
        $metricsJson.failure_reason = "Max attempts ($maxAttempts) exceeded"
    }
    
    # Stop conditions
    if ($consecutiveFailures -ge $maxConsecutiveFailures) {
        Write-Host ""
        Write-Host "STOP: $maxConsecutiveFailures consecutive failures" -ForegroundColor Red
        break
    }
}

$endTime = Get-Date
$metricsJson.end_time = $endTime.ToString("yyyy-MM-ddTHH:mm:ss")
Update-Metrics

# Final report
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "       EXECUTION LOOP REPORT" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Run: $Run" -ForegroundColor White
Write-Host "Total tasks: $($tasks.Count)" -ForegroundColor White
Write-Host "Completed: $completed" -ForegroundColor Green
Write-Host "Failed: $failed" -ForegroundColor Red
if ($completed + $failed -gt 0) {
    $successRate = [math]::Round(($firstSuccess / ($completed + $failed)) * 100, 1)
    Write-Host "First attempt success: $successRate%" -ForegroundColor White
}
$totalTime = [math]::Round($totalTime, 1)
Write-Host "Total time: ${totalTime}s" -ForegroundColor White
if ($completed -gt 0) {
    $avgTime = [math]::Round($totalTime / $completed, 1)
    Write-Host "Avg time/task: ${avgTime}s" -ForegroundColor White
}
Write-Host "Failed at: $($metricsJson.failed_at)" -ForegroundColor White
Write-Host "Reason: $($metricsJson.failure_reason)" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
