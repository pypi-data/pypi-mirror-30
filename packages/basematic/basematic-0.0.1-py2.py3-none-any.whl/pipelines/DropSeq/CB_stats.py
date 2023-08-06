from basematic.pipelines.Node_Pipeline import node_pipeline

node = node_pipeline("CBStata")
node.desc = "Correct the Barcode and generate the distribution of read counts"

#Add Inputs


# Add Output
node.add_output("valid_CB", "int")
node.add_output("valid_CB_counts", "int")

