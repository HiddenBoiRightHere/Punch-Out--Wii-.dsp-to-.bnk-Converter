import struct
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo


# Create a window.
#root = tk.Tk()
#root.geometry("500x300")
#root.title(string="Main window for File selection and operation.")
#Fun = tk.Label(text="what a thing")
#Fun.pack()

# 1. Open files. One will be designated "input audio" and "file to overwrite"
#Open two files. "rb" defines "read" and "binary"
wem_original = open(r"w1ch.wem", "rb")
dsp_replacing = open(r"1chSAME.dsp", "rb")


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


# 2. Determine whether input audio and output audio are of the same channels. If not, tell user to go fix it.
#Compares if files have the same set of channels.

if w_o == "2e" and d_r == "0000":
    print("These one-channel files' channels are compatible.")
    wem_original.seek(0xDC)
    wem_originalDataLength = wem_original.read(4)
elif w_o == "5c" and d_r == "0204":
    print("These two-channel files' channels are compatible.")
    wem_original.seek(0xFC)
    wem_originalDataLength = wem_original.read(4)
else:
    print("These files' channels are not compatible.")
    exit()




# 3. Determine whether input audio length is too long for overwritten file. If so, give warning to user that it will be cut off if continued.
#Compares the audio lengths determined by the data tag.

#Finds data length of wem files


#Finds data length of .dsp files

dsp_replacing.seek(0x00)
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
elif dsp_replacingInt == wem_originalInt:
    print("Your file is exactly the same size!")
    same = 1
else:
    large = 1
    print("Your .wem file allows more data than your dsp file provides. Please note that additional null values of silence will replace the necessary length needed.")
    print("large")

# 4. Determine whether overwritten file length is too short to create a file. (Note to self as well, check to see if these can be edited at all if they are shorter than 2000, which a lot of them are. But that's for another time maybe. WAIT IF IT'S ONE CHANNEL IT DOESN'T NEED INTERLEAVE DOES IT I'M SO DUMB- I will test that again later and take note) If so, tell user to deal with it. :(
#if size of wem is smaller than 2000, use stacking only for now and warn user (needs to be tested)




# 5. Once all the basic checks are done, begin taking out the necessary data. The coefficient(s) which depend on channels and actual audio data.
#create new file that is exact copy of wem

wemOutputFile = open(r"wemOutFile.wem", "wb")
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

if d_r == "5C":
    dsp_replacing.seek(0x7C)
    dspReadInOutCoefficients = dsp_replacing.read(0x2E)
    wemOutputFile.seek(0xB6)
    wemOutputFile.write(dspReadInOutCoefficients)
else:
    pass







#split into blocks of 2000. if less than 2000, stack and warn user.
if w_o == "2e":
    dsp_replacing.seek(0x60)
else:
    dsp_replacing.seek(0xC0)
i = 1

chunk_size = 0x2000
chunk = dsp_replacing.read(chunk_size)
oddByteCollection = open(r"oddByteList", "wb")


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

oddByteCollectionWrite = open(r"oddByteList", "rb")
evenByteCollectionWrite = open(r"evenByteList", "rb")

oddByteCollectionWrite.seek(0x0)
evenByteCollectionWrite.seek(0x0)



#determine if interleave is necessary, then choose to interleave.
if w_o == "2e":
    fullCollection = open(r"totalList", "wb")
    dsp_replacing.seek(0x60)
    dspDataSC = dsp_replacing.read()
    fullCollection.write(dspDataSC)
    fullCollection.close()
    fullCollectionWriter = open(r"totalList", "rb")
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



#10. Tell user to go implant it into where it needs to go in the .bnk file with BNKEditor.
#show user instructions. also create button for this on main window.

# 10a. Or become the biggest brain ever and write it myself using analysis of the DIDX section but I'm dumb dumb and this is already getting hard to automate for my poor brain.
#hold off on this for now.

#root.mainloop()
