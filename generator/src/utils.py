import subprocess
from pathlib import Path
from git import Optional, RemoteProgress
from rich.progress import Progress, TextColumn, BarColumn, FileSizeColumn, TransferSpeedColumn, TimeRemainingColumn, SpinnerColumn

class RichCloneProgress(RemoteProgress):
    def __init__(self):
        super().__init__()
        self.progress = Progress(
            TextColumn("[bold blue]{task.fields[filename]}", justify="right"),
            BarColumn(bar_width=None),
            "[progress.percentage]{task.percentage:>3.1f}%",
            "•",
            FileSizeColumn(),
            "•",
            TransferSpeedColumn(),
            "•",
            TimeRemainingColumn(),
        )
        self.tasks = {}
        self.progress.start()

    def update(self, op_code, cur_count, max_count=None, message=''):
        if not max_count:
            max_count = cur_count

        if op_code & self.BEGIN:
            description = message or "Processing"
            task_id = self.progress.add_task(description, total=float(max_count), filename=description)
            self.tasks[op_code & self.OP_MASK] = task_id // 1
        
        task_id = self.tasks.get(op_code & self.OP_MASK)
        
        if task_id is not None and max_count:
            self.progress.update(task_id, completed=float(cur_count), total=float(max_count))
            
        if op_code & self.END:
             if task_id is not None:
                self.progress.update(task_id, completed=float(max_count))
    
    def __call__(self, op_code, cur_count, max_count=None, message=''):
        return self.update(op_code, cur_count, max_count, message)

    def __del__(self):
        if hasattr(self, 'progress'):
            self.progress.stop()

def run_process_with_progress(cmd: list[str], description: str, cwd: Optional[Path | str] = None) -> int:
    with subprocess.Popen(
        cmd, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.STDOUT, 
        text=True, 
        bufsize=1,
        cwd=cwd
    ) as process:
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            transient=True
        ) as progress:
            task = progress.add_task(description, total=None)
            stdout = process.stdout
            if not stdout:
                return process.returncode
            for line in stdout:
                line = line.strip()
                if line:
                    if line.startswith("Compiling") or line.startswith("Finished"):
                        progress.console.print(line)
                    else:
                        progress.update(task, description=f"{line[:60]}...")
    return process.returncode