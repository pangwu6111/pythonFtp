<#
.SYNOPSIS
    FTP断点续传下载工具 - PowerShell版本

.DESCRIPTION
    支持断点续传的FTP文件下载工具，适用于Windows环境

.PARAMETER Url
    FTP服务器URL (格式: ftp://user:pass@host:port/path/file)

.PARAMETER Output
    本地保存路径

.PARAMETER ChunkSize
    下载块大小 (默认: 8192字节)

.PARAMETER MaxRetries
    最大重试次数 (默认: 3次)

.PARAMETER Timeout
    连接超时时间 (默认: 30秒)

.PARAMETER ListFiles
    列出远程目录文件

.EXAMPLE
    .\ftp_download.ps1 -Url "ftp://ftp.example.com/pub/file.zip"

.EXAMPLE
    .\ftp_download.ps1 -Url "ftp://user:pass@ftp.example.com/file.zip" -Output "D:\Downloads\file.zip"

.EXAMPLE
    .\ftp_download.ps1 -Url "ftp://ftp.example.com/pub/" -ListFiles
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$Url,
    
    [string]$Output,
    
    [int]$ChunkSize = 8192,
    
    [int]$MaxRetries = 3,
    
    [int]$Timeout = 30,
    
    [switch]$ListFiles
)

# 设置控制台编码为UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

function Write-ColorText {
    param(
        [string]$Text,
        [ConsoleColor]$Color = [ConsoleColor]::White
    )
    Write-Host $Text -ForegroundColor $Color
}

function Format-FileSize {
    param([long]$Size)
    
    $units = @('B', 'KB', 'MB', 'GB', 'TB')
    $index = 0
    $size = [double]$Size
    
    while ($size -ge 1024 -and $index -lt $units.Length - 1) {
        $size /= 1024
        $index++
    }
    
    return "{0:N1}{1}" -f $size, $units[$index]
}

function Format-TimeSpan {
    param([TimeSpan]$TimeSpan)
    
    if ($TimeSpan.TotalSeconds -lt 60) {
        return "{0:N0}秒" -f $TimeSpan.TotalSeconds
    } elseif ($TimeSpan.TotalMinutes -lt 60) {
        return "{0:N0}分{1:N0}秒" -f $TimeSpan.TotalMinutes, $TimeSpan.Seconds
    } else {
        return "{0:N0}时{1:N0}分" -f $TimeSpan.TotalHours, $TimeSpan.Minutes
    }
}

function Show-Progress {
    param(
        [long]$Downloaded,
        [long]$Total,
        [DateTime]$StartTime
    )
    
    $percent = ($Downloaded / $Total) * 100
    $elapsed = (Get-Date) - $StartTime
    $speed = if ($elapsed.TotalSeconds -gt 0) { $Downloaded / $elapsed.TotalSeconds } else { 0 }
    
    $eta = if ($speed -gt 0) { 
        [TimeSpan]::FromSeconds(($Total - $Downloaded) / $speed)
    } else { 
        [TimeSpan]::Zero 
    }
    
    $progressBar = "█" * [int]($percent / 2) + "░" * (50 - [int]($percent / 2))
    
    $status = "[{0}] {1:F1}% {2}/{3} 速度: {4}/s ETA: {5}" -f 
        $progressBar, $percent, 
        (Format-FileSize $Downloaded), (Format-FileSize $Total),
        (Format-FileSize $speed), (Format-TimeSpan $eta)
    
    Write-Host "`r$status" -NoNewline
}

function Download-FtpFileWithResume {
    param(
        [string]$FtpUrl,
        [string]$LocalPath,
        [int]$ChunkSize,
        [int]$MaxRetries,
        [int]$Timeout
    )
    
    # 解析FTP URL
    try {
        $uri = [System.Uri]$FtpUrl
        if ($uri.Scheme -ne 'ftp') {
            throw "URL必须以ftp://开头"
        }
    } catch {
        Write-ColorText "✗ 无效的FTP URL: $FtpUrl" Red
        return $false
    }
    
    # 确定本地文件路径
    if (-not $LocalPath) {
        $LocalPath = Split-Path $uri.AbsolutePath -Leaf
    }
    
    $localFile = [System.IO.FileInfo]$LocalPath
    if (-not $localFile.Directory.Exists) {
        $localFile.Directory.Create()
    }
    
    Write-ColorText "📁 远程文件: $($uri.AbsolutePath)" Cyan
    Write-ColorText "💾 本地文件: $LocalPath" Cyan
    
    $retries = 0
    while ($retries -lt $MaxRetries) {
        try {
            # 获取远程文件大小
            $sizeRequest = [System.Net.FtpWebRequest]::Create($FtpUrl)
            $sizeRequest.Method = [System.Net.WebRequestMethods+Ftp]::GetFileSize
            $sizeRequest.Timeout = $Timeout * 1000
            
            if ($uri.UserInfo) {
                $credentials = $uri.UserInfo.Split(':')
                $sizeRequest.Credentials = New-Object System.Net.NetworkCredential($credentials[0], $credentials[1])
            }
            
            $sizeResponse = $sizeRequest.GetResponse()
            $remoteSize = $sizeResponse.ContentLength
            $sizeResponse.Close()
            
            Write-ColorText "📊 远程文件大小: $(Format-FileSize $remoteSize)" Green
            
            # 检查本地文件
            $localSize = 0
            if ($localFile.Exists) {
                $localSize = $localFile.Length
                if ($localSize -eq $remoteSize) {
                    Write-ColorText "✓ 文件已完整下载" Green
                    return $true
                } elseif ($localSize -gt $remoteSize) {
                    Write-ColorText "✗ 本地文件大小异常，重新下载" Yellow
                    $localFile.Delete()
                    $localSize = 0
                }
            }
            
            if ($localSize -gt 0) {
                Write-ColorText "🔄 断点续传，从 $(Format-FileSize $localSize) 开始" Yellow
            }
            
            # 创建下载请求
            $request = [System.Net.FtpWebRequest]::Create($FtpUrl)
            $request.Method = [System.Net.WebRequestMethods+Ftp]::DownloadFile
            $request.Timeout = $Timeout * 1000
            $request.ContentOffset = $localSize
            
            if ($uri.UserInfo) {
                $credentials = $uri.UserInfo.Split(':')
                $request.Credentials = New-Object System.Net.NetworkCredential($credentials[0], $credentials[1])
            }
            
            # 开始下载
            $response = $request.GetResponse()
            $responseStream = $response.GetResponseStream()
            
            $fileMode = if ($localSize -gt 0) { [System.IO.FileMode]::Append } else { [System.IO.FileMode]::Create }
            $fileStream = New-Object System.IO.FileStream($LocalPath, $fileMode)
            
            $buffer = New-Object byte[] $ChunkSize
            $downloaded = $localSize
            $startTime = Get-Date
            
            try {
                while ($true) {
                    $bytesRead = $responseStream.Read($buffer, 0, $ChunkSize)
                    if ($bytesRead -eq 0) { break }
                    
                    $fileStream.Write($buffer, 0, $bytesRead)
                    $downloaded += $bytesRead
                    
                    # 显示进度
                    if ($downloaded % ($ChunkSize * 10) -eq 0 -or $downloaded -eq $remoteSize) {
                        Show-Progress $downloaded $remoteSize $startTime
                    }
                }
                
                Write-Host ""
                
                if ($downloaded -eq $remoteSize) {
                    Write-ColorText "✓ 下载完成: $LocalPath" Green
                    return $true
                } else {
                    Write-ColorText "✗ 下载不完整: $downloaded/$remoteSize" Red
                    return $false
                }
                
            } finally {
                $fileStream.Close()
                $responseStream.Close()
                $response.Close()
            }
            
        } catch {
            $retries++
            Write-ColorText "✗ 下载失败 (尝试 $retries/$MaxRetries): $($_.Exception.Message)" Red
            
            if ($retries -lt $MaxRetries) {
                Write-ColorText "🔄 等待重试..." Yellow
                Start-Sleep -Seconds 2
            }
        }
    }
    
    Write-ColorText "✗ 达到最大重试次数，下载失败" Red
    return $false
}

function Get-FtpDirectoryListing {
    param(
        [string]$FtpUrl,
        [int]$Timeout
    )
    
    try {
        $uri = [System.Uri]$FtpUrl
        
        $request = [System.Net.FtpWebRequest]::Create($FtpUrl)
        $request.Method = [System.Net.WebRequestMethods+Ftp]::ListDirectoryDetails
        $request.Timeout = $Timeout * 1000
        
        if ($uri.UserInfo) {
            $credentials = $uri.UserInfo.Split(':')
            $request.Credentials = New-Object System.Net.NetworkCredential($credentials[0], $credentials[1])
        }
        
        $response = $request.GetResponse()
        $responseStream = $response.GetResponseStream()
        $reader = New-Object System.IO.StreamReader($responseStream)
        
        $listing = @()
        while (-not $reader.EndOfStream) {
            $listing += $reader.ReadLine()
        }
        
        $reader.Close()
        $responseStream.Close()
        $response.Close()
        
        return $listing
        
    } catch {
        Write-ColorText "✗ 获取目录列表失败: $($_.Exception.Message)" Red
        return @()
    }
}

# 主程序
try {
    Write-ColorText "🚀 FTP断点续传下载工具" Cyan
    Write-ColorText "================================" Cyan
    
    if ($ListFiles) {
        Write-ColorText "📂 获取远程目录列表..." Yellow
        $files = Get-FtpDirectoryListing $Url $Timeout
        
        if ($files.Count -gt 0) {
            Write-ColorText "`n📂 远程目录内容:" Green
            foreach ($file in $files) {
                Write-Host "  $file"
            }
        } else {
            Write-ColorText "📂 目录为空或无法访问" Yellow
        }
    } else {
        $success = Download-FtpFileWithResume $Url $Output $ChunkSize $MaxRetries $Timeout
        
        if (-not $success) {
            exit 1
        }
    }
    
} catch {
    Write-ColorText "✗ 发生错误: $($_.Exception.Message)" Red
    exit 1
}