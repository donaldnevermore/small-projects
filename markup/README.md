# How to use

On Linux/MacOS

```bash
poetry run python markup.py < test_input.txt > test_output.html
```

On Windows

```powershell
Get-Content test_input.txt | poetry run python markup.py | Set-Content test_output.html
```
