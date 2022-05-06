import tkinter as tk
from tkinter import filedialog as fd
import os


# Create a window.
root = tk.Tk()
root.geometry("600x400")
root.title(string=".dsp to .wem File Importer")
Fun = tk.Label(text="Please press each button in order from top to bottom. Note that this only works for 2-channel files, as 1-channel files are still under development. Use BNKEditor to place your output files in your intended final destination.", wraplength=500)
Fun.pack()



#buttons for getting filenames
def wemFileLocation():
    global file_path
    file_path = fd.askopenfilename(title="Select A File", filetypes=(
    ("Original .wav file", "*.wav"), ("WEM File", "*.wem"), ("Any Type", "*.*")))
    l1.configure(text="File path for wem: " + file_path)
    return file_path


def dspFileLocation():
    global file_path2
    file_path2 = fd.askopenfilename(title="Select A File", filetypes=(
        ("Original .dsp file", "*.dsp"), ("Interleaved .idsp File", "*.idsp"), ("Any Type", "*.*")))
    l2.configure(text="File path for dsp: " + file_path2)
    return file_path2

def outputDestination():
    global file_path3
    file_path3 = fd.askdirectory(title="Select a Folder")
    l3.configure(text="File path for output:" + file_path3)
    return file_path3

wemOpener = tk.Button(root, text = "Punch-Out!! Wii Wem File", command = wemFileLocation).pack()
dspOpener = tk.Button(root, text = "VGAudio DSP File", command = dspFileLocation).pack()
outputLocation = tk.Button(root, text = "Output folder for new Wem file", command = outputDestination).pack()



def OrganizerFull():


    # Open two files. "rb" defines "read" and "binary"
    wem_original = open(file_path, "rb")
    dsp_replacing = open(file_path2, "rb")

    #Find value at offset 0x87 for both 1 and 2 channels for wem.
    wem_original.seek(0x87)
    wem_originalChannelByte = wem_original.read(1)


    #Print value at offset 0x87 for both 1 and 2 channels for wem.
    w_o = wem_originalChannelByte.hex()
    print(w_o)



    #Find value at offset 0x4B for both 1 and 2 channels for dsp.
    dsp_replacing.seek(0x4B)
    dsp_replacingChannelBytes = dsp_replacing.read(2)

    #Print value at offset 0x4B for both 1 and 2 channels for dsp.
    d_r = dsp_replacingChannelBytes.hex()
    print(d_r)


    #Compares if files have the same set of channels.

    if w_o == "2e" and d_r == "0000":
        print("These one-channel files' channels are compatible.")
        wem_original.seek(0xDC)
        wem_originalDataLength = wem_original.read(4)
        progressLabel = tk.Label(root, text = "These one-channel files' channels are compatible.")
        progressLabel.pack()
    elif w_o == "5c" and d_r == "0204":
        print("These two-channel files' channels are compatible.")
        wem_original.seek(0xFC)
        wem_originalDataLength = wem_original.read(4)
        progressLabel = tk.Label(root, text="These two-channel files' channels are compatible.")
        progressLabel.pack()
    else:
        print("These files' channels are not compatible.")
        progressLabel = tk.Label(root, text="These one-channel files' channels are compatible. Press the button below to exit.")
        progressLabel.pack()
        var = tk.IntVar()
        WaitConfirmation = tk.Button(root, text="Okay", command=lambda: var.set(1))
        WaitConfirmation.pack()
        root.wait_variable(var)
        WaitConfirmation.pack_forget()
        print("Exiting.")
        exit()




    #Compares the audio lengths determined by the data tag.

    #Finds data length of wem files


    #Finds data length of .dsp files

    dsp_replacing.seek(0x04)
    dsp_replacingDataLength = dsp_replacing.read(4)
    #Converts byte size of file information into integers.

    wem_originalInt = int.from_bytes(wem_originalDataLength, byteorder='big')
    print(wem_originalInt)
    dsp_replacingInt = int.from_bytes(dsp_replacingDataLength, byteorder='big')
    print(dsp_replacingInt)


    #if statement for calculating size
    #if size of dsp > size of wem, give user a warning but ability to proceed.


    small = 0
    same = 0
    large = 0

    if dsp_replacingInt > wem_originalInt:
        print("Your .wem file allows less data than your .dsp file. Please note that your data will be cut off. Continue?")
        small = 1
        print("small")

        warnText = tk.Label(root, text = "Your .wem file allows less data than your .dsp file. Please note that your data will be cut off. Continue?", wraplength=500)
        warnText.pack()
        var = tk.IntVar()
        WaitConfirmation = tk.Button(root, text="Okay", command=lambda: var.set(1))
        WaitConfirmation.pack()
        print("Continue?")
        root.wait_variable(var)
        WaitConfirmation.pack_forget()
        print("Continuing.")

    elif dsp_replacingInt == wem_originalInt:
        warnText = tk.Label(root, text = "Your file is exactly the same size!")
        warnText.pack()
        same = 1
    else:
        large = 1
        print("Your .wem file allows more data than your dsp file provides. Please note that additional null values of silence will replace the necessary length needed.")
        print("large")
        warnText = tk.Label(root, text="Your .wem file allows more data than your dsp file provides. Please note that additional null values of silence will replace the necessary length needed. Continue?", wraplength=500)
        warnText.pack()
        var = tk.IntVar()
        WaitConfirmation = tk.Button(root, text="Okay", command=lambda: var.set(1))
        WaitConfirmation.pack()
        print("Continue?")
        root.wait_variable(var)
        WaitConfirmation.pack_forget()
        print("Continuing.")

    #4. Determine whether overwritten file length is too short to create a file. (as I'm tired of this, it is a feature that will have to wait.)
    #if size of wem is smaller than 2000, use stacking only for now and warn user (needs to be tested)




    # 5. Once all the basic checks are done, begin taking out the necessary data. The coefficient(s) which depend on channels and actual audio data.
    #create new file that is exact copy of wem

    wemOutputFile = open(file_path3 + r"/wemOutFile.wem", "wb")
    wem_original.seek(0x0)

    if w_o == "2e":
        wemReadInOutHeaders = wem_original.read(0xE0)
        wemOutputFile.write(wemReadInOutHeaders)
    else:
        wemReadInOutHeaders = wem_original.read(0x100)
        wemOutputFile.write(wemReadInOutHeaders)


    #read and save coefficients from dsp

    dsp_replacing.seek(0x1C)
    dspReadInOutCoefficients = dsp_replacing.read(0x2E)
    # write coefficients into new wem
    wemOutputFile.seek(0x88)
    wemOutputFile.write(dspReadInOutCoefficients)

    if w_o == "5c":
        dsp_replacing.seek(0x7C)
        dspReadInOutCoefficients = dsp_replacing.read(0x2E)
        wemOutputFile.seek(0xB6)
        wemOutputFile.write(dspReadInOutCoefficients)
    else:
        pass







    #split into blocks of 2000. if less than 2000, stack and warn user. (or well, too bad, I won't warn you about it.)
    if w_o == "2e":
        dsp_replacing.seek(0x60)
    else:
        dsp_replacing.seek(0xC0)
    i = 1

    chunk_size = 0x2000
    chunk = dsp_replacing.read(chunk_size)
    oddByteCollection = open(file_path3 + r"\oddByteList", "wb")
    evenByteCollection = open(file_path3 + r"\evenByteList", "wb")


    while chunk:
        if (i % 2) == 1:
            oddByteCollection.write(chunk)
            chunk = dsp_replacing.read(chunk_size)
            i = i + 1
        else:
            evenByteCollection.write(chunk)
            chunk = dsp_replacing.read(chunk_size)
            i = i + 1



    #close files to allow reading later
    oddByteCollection.close()
    evenByteCollection.close()

    oddByteCollectionWrite = open(file_path3 + r"\oddByteList", "rb")
    evenByteCollectionWrite = open(file_path3 + r"\evenByteList", "rb")

    oddByteCollectionWrite.seek(0x0)
    evenByteCollectionWrite.seek(0x0)



    #determine if interleave is necessary, then choose to interleave.
    if w_o == "2e":
        fullCollection = open(file_path3 + r"\totalList", "wb")
        dsp_replacing.seek(0x60)
        dspDataSC = dsp_replacing.read()
        fullCollection.write(dspDataSC)
        fullCollection.close()
        fullCollectionWriter = open(file_path3 + r"\totalList", "rb")
        fullCollectionWriterFiller = fullCollectionWriter.read()
    #write only necessary data
    totalOdd = oddByteCollectionWrite.read()
    totalEven = evenByteCollectionWrite.read()


    if w_o == "2e":
        wemOutputFile.seek(0xE0)
    else:
        wemOutputFile.seek(0x100)




    # 7. Implant replacing data into the file.
    #determines what to write into output file based on size
    #large means that the wem file will accept more bytes, thus nulls need to fill in the blanks
    if large == 1:
        wemOutputFile.write(totalOdd)
        wemOutputFile.write(totalEven)
        totalExtraNull = wem_originalInt - dsp_replacingInt
        nullCounter = 0
        while nullCounter < totalExtraNull:
            wemOutputFile.write(b"\x00")
            nullCounter = nullCounter + 1
    elif small == 1:
        #small means that the wem cannot take all the bytes, thus the file must cut off the data.
        #find the limit
        differenceLarge = dsp_replacingInt - wem_originalInt
        writeTotal = wem_originalInt // 2
        #split into odd and even chunks
        oddByteCollectionWrite.seek(0x0)
        evenByteCollectionWrite.seek(0x0)
        largeOdd = oddByteCollectionWrite.read(writeTotal)
        largeEven = evenByteCollectionWrite.read(writeTotal)
        #write into file stacked at max length
        wemOutputFile.write(largeOdd)
        wemOutputFile.write(largeEven)
    else:
        #same, so write it all out.
        wemOutputFile.write(totalOdd)
        wemOutputFile.write(totalEven)

    oddByteCollectionWrite.close()
    evenByteCollectionWrite.close()
    os.remove(file_path3 + r"/oddByteList")
    os.remove(file_path3 + r"/evenByteList")

    if w_o == "2e":
        os.remove(file_path3 + r"/totalList")
    else:
        pass


    print("done")
    endingText = tk.Label(root, text = "The process is complete. See WemOutFile.wem as your result. Press okay to reset text.")
    endingText.pack()
    waitVar = tk.IntVar()
    clearScreen = tk.Button(root, text="Okay", command=lambda: waitVar.set(1))
    clearScreen.pack()
    root.wait_variable(waitVar)
    clearScreen.pack_forget()
    endingText.pack_forget()
    warnText.pack_forget()
    progressLabel.pack_forget()

    #10. Tell user to go implant it into where it needs to go in the .bnk file with BNKEditor.
    #show user instructions. also create button for this on main window.

    # 10a. Or become the biggest brain ever and write it myself using analysis of the DIDX section but I'm dumb dumb and this is already getting hard to automate for my poor brain.
    #hold off on this for now.
runOrg = tk.Button(root, text = "Run", command = OrganizerFull).pack()


l1 = tk.Label(root, text="File path for wem: Not yet defined.")
l1.pack()
l2 = tk.Label(root, text="File path for dsp: Not yet defined")
l2.pack()
l3 = tk.Label(root,text="File path for output: Not yet defined")
l3.pack()

root.mainloop()


