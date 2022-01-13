Task default -depends Build

Task Restore {
    Exec { python -m pip install --upgrade build twine }
}

Task Rebuild {
    $readme = $(Get-Childitem "README.md")[0]

    Set-Location src/main
    Write-Output "📦 Build main"

    Copy-Item $readme ./README.md
    Exec { python -m build -o ../../dist }
    Remove-Item ./README.md
    
    Set-Location ../..
}

Task Build -depends Restore, Rebuild

Task DeployBuilt {
    Exec { python -m twine upload --skip-existing --repository pypi "dist/*" }
}

Task Deploy -depends Build, DeployBuilt

Task Install {

    Write-Output "🛠 Install dependencies"
    if ([System.Runtime.InteropServices.RuntimeInformation]::IsOSPlatform([System.Runtime.InteropServices.OSPlatform]::Linux)) {
        Exec { sudo apt-get update >/dev/null }
    }
    elseif ([System.Runtime.InteropServices.RuntimeInformation]::IsOSPlatform([System.Runtime.InteropServices.OSPlatform]::OSX)) {
    }
    elseif ([System.Runtime.InteropServices.RuntimeInformation]::IsOSPlatform([System.Runtime.InteropServices.OSPlatform]::Windows)) {
    }

    Write-Output "🛠 Install main"

    Set-Location ./dist
    Exec { python -m pip install $(Get-Childitem "coxbuild-*.whl")[0] }

    Set-Location ..
}

Task Uninstall {
    Write-Output "⚒ Uninstall main"

    Set-Location ./dist
    Exec { python -m pip uninstall $(Get-Childitem "coxbuild*.whl")[0] -y }

    Set-Location ..
}

Task Demo {
    Write-Output "⏳ 1️⃣ Version ⏳"
    Exec { coxbuild --version }
    Write-Output "⏳ 2️⃣ Help ⏳"
    Exec { coxbuild --help }
}

Task Test -depends Install, Demo, Uninstall

Task Clean {
    Remove-Item -Recurse ./dist
    foreach ($egg in Get-Childitem -Recurse *.egg-info) {
        Write-Output "🗑 Remove $egg"
        Remove-Item -Recurse $egg
    }
}

Task Format {
    autopep8 -r --in-place ./src

    foreach ($file in Get-Childitem "./src/**/*.py" -Recurse) {
        isort $file
    }
}