# **Remote DLL Injection (Windows)**

Remote DLL injection is a technique used to run code within the address space of another process by injecting a DLL into it. This is commonly used for extending or altering the behavior of a program, debugging, or, unfortunately, in malicious software for executing payloads within the context of legitimate processes to hide its presence.

The basic steps involved in remote DLL injection include:

1. **Open the Target Process**: Obtain a handle to the target process with sufficient privileges to modify its memory and create threads.
2. **Allocate Memory in the Target Process**: Reserve and commit memory within the target process's address space to store the path of the DLL to be injected.
3. **Write the DLL Path into the Allocated Memory**: Copy the path of the DLL into the allocated memory region within the target process.
4. **Execute `LoadLibrary` in the Context of the Target Process**: Create a remote thread in the target process that calls `LoadLibrary`, passing the address of the memory containing the DLL path. `LoadLibrary` loads the DLL into the process, executing its `DllMain`.
5. **Clean up**: Free the allocated memory and close handles to maintain system stability and security.

## Disclaimer

The tools and scripts provided in this repository are made available for educational purposes only and are intended to be used for testing and protecting systems with the consent of the owners. The author does not take any responsibility for the misuse of these tools. It is the end user's responsibility to obey all applicable local, state, national, and international laws. The developers assume no liability and are not responsible for any misuse or damage caused by this program. Under no circumstances should this tool be used for malicious purposes. The author of this tool advocates for the responsible and ethical use of security tools. Please use this tool responsibly and ethically, ensuring that you have proper authorization before engaging any system with the techniques demonstrated by this project.

## Features
- **remote_dll_injection.py**: This Python script automates the process of remote DLL injection for a specified process ID (PID) and a given DLL.
- **remote_dll_injection.c**: This C program is a simple Windows Dynamic Link Library (DLL) that demonstrates using the `DllMain`function, which is a mandatory entry point for every DLL. This function is called by the Windows operating system whenever the DLL is loaded into a process, unloaded from a process, threads are created within the process, or threads within the process are destroyed. The purpose of this particular DLL is to display a message box when it is injected into a process.

  ## Prerequisites

- **Operating System**: Tested on Windows, version 10 22H2.
- **Python Version**: Python 3.6+
- **Visual Studio 2022**: For compiling the custom DLL using the provided C code.
- **Administrator Privileges**: Required to perform operations such as writing to another process's memory space.
- **ctypes**: A Python library used for foreign function interface.

## Installation

1. **Python Setup**: Ensure Python is installed on your system. If not already installed, download and install it from the [official Python website](https://www.python.org/downloads/).
2. **Visual Studio 2022**:
    - Install Visual Studio 2022 with the Desktop development with C++ workload, which includes necessary compilers and the Windows SDK.
    - Ensure the latest updates for Visual Studio and the installed components are applied.
      ![Visual Studio 2022 C++](/images/visual_studio_2022.png)
    
3. **Verify Administrative Privileges**: Ensure your user account has administrative privileges to perform DLL injection. This may require running scripts or Visual Studio as an administrator.

## Usage

### Compile Custom DLL (Visual Studio 2022)

1. **Create a New Project:**
    - Open Visual Studio 2022.
    - Select "Create a new project" from the initial dashboard.
    - In the "Create a new project" window, choose "C++" as the language and "Windows" as the platform from the filters, then select "Dynamic-Link Library (DLL)" from the list of templates, and click "Next".
    - Give your project a name, for example, "CustomDLL", and choose a location to save it. Click "Create".
2. **Add Your C Code to the Project:**
    - Visual Studio creates a DLL project with some default files. You can either modify the existing `dllmain.cpp` file or add a new C file to the project.
    - To add a new file, right-click on the "Source Files" folder in the "Solution Explorer" pane, select "Add" > "New Item".
    - Choose "C++ File (.cpp)", name it (e.g., `CustomDLL.c`), and click "Add".
    - Copy and paste your provided C code into this file. Even though you're writing C code, using a `.cpp` extension is fine for C code in a C++ project, thanks to the `extern "C"` declaration which prevents C++ name mangling.
        
        <aside>
        ⚠️ If you compile a C program for a DLL without using `extern "C"` or `__declspec(dllexport)`, you should add a new item to your Visual Studio project with a `.c` extension instead of `.cpp`. This tells Visual Studio to treat the file as C code, not C++, which affects how the compiler interprets the code and can impact how symbols are exported or mangled. Delete the `dllmain.cpp` file if you plan to include the main function in your own code.
        
        </aside>
        
3. **Configure Project Properties:**
    - Right-click on your project in the "Solution Explorer" pane and select "Properties".
    - In the "Configuration Properties" > "General", ensure the "Configuration Type" is set to "Dynamic Library (.dll)".
    - Go to "C/C++" > "Precompiled Headers", and set "Precompiled Header" to "Not Using Precompiled Headers", if the provided code does not use them.
    - Click "Apply" and then "OK" to save the changes.
4. **Build the DLL:**
    - From the top menu, select "Build" > "Build Solution" to compile your DLL.
    - If there are no errors, Visual Studio compiles your code into a DLL named after your project (e.g., `CustomDLL.dll`).
    - The output DLL file is typically located in the `Debug` or `Release` folder within your project directory, depending on your build configuration.

### Python Script

1. **Configure the Python Script**: Update the `dll_path` variable in the Python script to point to the compiled DLL's location on your system.
2. **Run the Script**: Run the script and follow the on-screen prompts to enter the target process ID (PID).
    
    ```bash
    python3 remote_dll_injection.py
    ```
## How It Works

- **Import Statements**: The script imports necessary functions and types from the `ctypes` module, which allows Python to call C functions and manipulate low-level data types required for Windows API calls.
- **`SECURITY_ATTRIBUTES` Structure**: Defines a structure to set security attributes for objects created by the script. It's part of the preparations for creating a remote thread but isn't explicitly used with default values.
- **Constants**: Define various constants used in Windows API calls, such as access rights, memory allocation types, and flags.
- **Function Declarations**: Specify argument types (`argtypes`) and return types (`restype`) for Windows API functions used in the script. This ensures type safety and clearer errors when calling these functions.
- **DLL Path**: Specifies the absolute path to the DLL to be injected. It's important this path is accessible by the target process.
- **Open Process**: Uses `OpenProcess` to obtain a handle to the target process identified by PID, with `PROCESS_ALL_ACCESS` rights.
- **Allocate Memory**: Calls `VirtualAllocEx` to allocate memory in the target process's address space, making room for the DLL path.
- **Write DLL Path**: Uses `WriteProcessMemory` to write the DLL path into the allocated memory within the target process.
- **Load Library Address**: Retrieves the address of the `LoadLibraryA` function from `kernel32.dll`, which is used to load the DLL into the target process.
- **Create Remote Thread**: Initiates `CreateRemoteThread` to create a thread in the target process. This thread calls `LoadLibraryA` with the address of the DLL path as its argument, causing the DLL to be loaded and executed within the target process.
- **Waiting for an Object**: Uses `WaitForSingleObject` to wait for the remote thread (created by `CreateRemoteThread` to load the DLL) to complete its execution. This ensures that any cleanup or further actions by the injector process occur only after the DLL has been fully loaded and executed in the target process.
- **Clean Up**: Frees the allocated memory and closes the handle to the target process to clean up resources.

## Output Example

```bash
Enter the target process ID (PID): 1676
Process Handle: 480
Remote Memory Allocated at: 0x27061430000
Bytes Written: 67
LoadLibraryA Address: 0x7FFA97230800
Remote Thread Created with ID: 508
```
![App Memory Address](/images/app_memory.png)
![Remote DLL Module](/images/remote_dll_module.png)
![kernel32 Load Library](/images/app_threads.png)
![Injected DLL Message](/images/custom_dll_success.png)

## Contributing

If you have an idea for an improvement or if you're interested in collaborating, you are welcome to contribute. Please feel free to open an issue or submit a pull request.

## License

This file is part of Remote DLL Injection.

Remote DLL Injection is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

Remote DLL Injection is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with Remote DLL Injection. If not, see https://www.gnu.org/licenses/.
