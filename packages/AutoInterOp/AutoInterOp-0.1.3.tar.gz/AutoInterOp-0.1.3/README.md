# AutoInterOp

### Description
Automatically runs a number of Illumina InterOp processing tools on a
target MiSeq run folder. The folder should contain both an **InterOp** folder
and a **RunInfo.xml** file.

### Installation
```pip3 install AutoInterOp```

#### Dependencies
- InterOp==v1.1.2: _https://github.com/Illumina/interop/releases/download/v1.1.2/InterOp-1.1.2-Linux-GNU.tar.gz_
- gnuplot (`sudo apt install gnuplot`)

**NOTE:** All InterOp binaries must be added to your $PATH.

### Usage
```bash
Usage: AutoInterOp.py [OPTIONS]

Options:
  -r, --run_folder PATH     Path to an Illumina MiSeq run folder. This should
                            contain a SampleInfo.xml file and an InterOp
                            folder.  [required]
  -o, --output_folder PATH  Path to desired output folder. Defaults to the
                            same place as the specified run_folder.
  -z, --zip                 Set this flag to zip all output files into a
                            single archive available within your output folder.
  --help                    Show this message and exit.
  ```