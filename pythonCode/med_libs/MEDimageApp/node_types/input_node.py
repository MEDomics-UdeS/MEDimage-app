import pickle
from ..node import Node
from ..MEDimageExtraction import UPLOAD_FOLDER
import MEDimage
from ..pipeline import Pipeline

class InputNode(Node):
    def __init__(self, params: dict):
        
        self.id = params['id']

        self.filepath = params['data']['filepath']
        
        self.output_obj = None
        
        self.scan_type = None
        
    def run(self, pipeline: Pipeline):
        # Load the MEDimg object from the input file
        with open(UPLOAD_FOLDER / self.filepath, 'rb') as f:
            MEDimg = pickle.load(f)
        MEDimg = MEDimage.MEDscan(MEDimg)
        
        # Check the scan type of the input image and format it to correspond with the pipeline im_params
        scan_type = MEDimg.type
        if scan_type == "PTscan":
            scan_type = "imParamPET"
        else:
            scan_type = "imParam" + scan_type[:-4]
        self.scan_type = scan_type
        
        # Update the im_params of the pipeline with the scan type
        pipeline.update_im_params()
        # Update the MEDimg object with the pipeline im_params
        MEDimage.MEDscan.init_params(MEDimg, pipeline.im_params)
        
        # Remove dicom header from MEDimg object as it causes errors in get_3d_view()
        # TODO: check if dicom header is needed in the future
        MEDimg.dicomH = None
        
        # Place the result in the output_obj attribute
        self.output_obj = MEDimg