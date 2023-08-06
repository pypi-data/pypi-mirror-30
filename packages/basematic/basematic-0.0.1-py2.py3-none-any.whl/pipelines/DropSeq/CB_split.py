from basematic.pipelines.Node_Pipeline import node_pipeline
import Data as DT

node = node_pipeline("barcode_split")
node.desc = "Split the Fastq file into 16 or 64 according to barcode prefix"

#Inputs
in_sample = node.add_input("sample", "sample", "", "")
in_path = node.add_input("path", "path", "", "")

#Outputs
node.add_output("datatype", DT.char)
node.add_output("counts", DT.int)
out_splitFiles = node.add_output("files", [DT.path])


