

import io
from ocad_grid_id_to_epsg import ocad_grid_id_2_epsg

#==============================================================================
# Sample functions
#==============================================================================

def _sample(path_file):
    """Docstring"""
    #if path given, opens the file, check if it is ocad
    file, file_close = _input_2_file_object(path_file)

    ###Code

    #if file is opend in this function/ close it know
    if file_close: file.close()
    return("?")

def _sample_string(path_file_string_dict):
    """Docstring"""
    #gets the list of all strings with the filterd typ
    string_list = _input_2_filterd_string_list(path_file_string_dict,filter=7)

    ###Code

    return("?")

#==============================================================================
# Own exceptions
#==============================================================================

class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class FileNotOcadError(Error):
    """Error raised when file isn't a OCAD-File"""

#==============================================================================
# Decode Functions
#==============================================================================

def _rhex(byte):
    """converts bytecode to hex, while reading from right to left"""
    rhex = byte[::-1].hex()
    return (rhex)

def _int_rhex(byte):
    """same as _rhex but returns integer instead of hex"""
    int_rhex = int(_rhex(byte),16)
    return (int_rhex)

def _string_dict(string):
    """splits a OCAD-string and returns a dict"""
    split_string = string.split("\t")
    i = 0
    string_dict = {}
    for codevalue in split_string:
        if i == 0:
            code = "First"
            value = codevalue
        else:
            code = codevalue[0:1]
            value = codevalue[1:]
        string_dict[code]=value
        i += 1
    return(string_dict)

def _boolean(string_int):
    """returns True or False, for 1 or 0"""
    if int(string_int) == 0:
        return(False)
    elif int(string_int) == 1:
        return(True)
    else:
        raise ValueError("Only 0 or 1 allowed")
#==============================================================================
# function diffrent input posibilitis to one
#==============================================================================

def _input_2_file_object(path_file):
    """converts a path or file-object to a file-object and set a variable if the file was opend her, for closing it later"""
    if isinstance(path_file, io.BufferedIOBase):
        file = path_file
        file_close = False
    else:
        file = file = open(path_file, "rb")
        file_close = True

    file.seek(0)
    if _rhex(file.read(2)) == "0cad":
        pass
    else:
        raise FileNotOcadError("This is not a OCAD-File")

    return (file, file_close)

def _input_2_filterd_string_list(path_file_string_dict,*,filter=None):
    """returns a filterd string list, from a path, flile-object or string-dict"""
    if type(path_file_string_dict) == dict:
        if filter in path_file_string_dict.keys():
            string_list = path_file_string_dict[filter]
        else:
            string_list = []
    else:
        #if path given, opens the file, check if it is ocad
        file, file_close = _input_2_file_object(path_file_string_dict)
        string_list = _get_ocad_strings(file, output_typ="list", filter=filter)
        #if file is opend in this function/ close it know
        if file_close: file.close()

    return(string_list)

#==============================================================================
# Public functions
#==============================================================================

def file_is_ocad(path_file):
    """Check if file is ocad"""
    try:
        file, file_close = _input_2_file_object(path_file)
        is_ocad = True
    except:
        is_ocad = False


    if file_close: file.close()

    return (is_ocad)

def file_is_map(path_file):
    """Check if file is ocad map file"""
    file, file_close = _input_2_file_object(path_file)


    is_map = _file_typ(file) == "map"

    #if file was opend in this function, then close it know
    if file_close:
        file.close()

    return (is_map)

def file_is_cs(path_file):
    """Check if file is ocad cours-setting file"""
    file, file_close = _input_2_file_object(path_file)


    is_cs = _file_typ(file) == "cs"

    #if file was opend in this function, then close it know
    if file_close:
        file.close()

    return (is_cs)

def file_version(path_file,*,format="short"):
    """returns the ocad file version"""
    file, file_close = _input_2_file_object(path_file)

    file.seek(4)
    if format == "short":
        version = str(_int_rhex(file.read(2)))
    elif format == "long":
        version = str(_int_rhex(file.read(2)))
        if int(version) <= 9:
            sub_version = str(_int_rhex(file.read(2)))
            version = version+"."+sub_version
        else:
            sub_version = str(_int_rhex(file.read(1)))
            sub_sub_version = str(_int_rhex(file.read(1)))
            version = version+"."+sub_version+"."+sub_sub_version

    if file_close: file.close()

    return (version)

def file_info(path_file):
    """returns a dict whit the file - information"""
    file, file_close = _input_2_file_object(path_file)
    string_dict = _get_ocad_strings(file, output_typ="dict")
    file_info = {}
    file_info["version_short"]=file_version(file)
    file_info["version_long"]=file_version(file,format="long")
    file_info["typ"]=_file_typ(file)
    file_info["note"]=_string_mapnote(string_dict)
    file_info["number_of_colors"]=_string_count_colors(string_dict)
    file_info["number_of_spot-colors"]=_string_count_spot_colors(string_dict)
    file_info["number_of_courses"]=_string_count_courses(string_dict)
    file_info["number_of_classes"]=_string_count_classes(string_dict)
    file_info["number_of_backgroundmaps"]=_string_count_backgroundmaps(string_dict)
    file_info["epsg_code"]=_string_epsg_code(string_dict)
    file_info["epsg_name"]=_string_epsg_name(string_dict)
    file_info["scale"]=_string_scale(string_dict)
    file_info["georeferenced"]=_string_georeferenced(string_dict)




    if file_close:
        file.close()

    return (file_info)

#==============================================================================
# Private Functions
#==============================================================================

def _file_typ(path_file):
    """returns the file-typ of a file"""
    #if path given, opens the file, check if it is ocad
    file, file_close = _input_2_file_object(path_file)

    type_dict = {0: "map", 1: "cs", 2: "map", 3: "cs" , 7: "map", 8: "server"}
    file.seek(2)
    file_type = _int_rhex(file.read(1))
    try:
        file_type = type_dict[file_type]
    except:
        file_type = file_type

    #if file is opend in this function/ close it know
    if file_close: file.close()
    return(file_type)

#==============================================================================
# Private String functions
#==============================================================================

def _string_mapnote(path_file_string_dict):
    """returns the map notes of the file"""
    #gets the list of all strings with the filterd typ
    string_list = _input_2_filterd_string_list(path_file_string_dict,filter=1061)
    if string_list == []:
        map_note = ""
    else:
        map_note = string_list[0]

    return(map_note)

def _string_count_colors(path_file_string_dict):
    """returns the number of colors"""
    #gets the list of all strings with the filterd typ
    string_list = _input_2_filterd_string_list(path_file_string_dict,filter=9)

    number_of_colors = len(string_list)

    return(number_of_colors)

def _string_count_spot_colors(path_file_string_dict):
    """returns the number of spot colors"""
    #gets the list of all strings with the filterd typ
    string_list = _input_2_filterd_string_list(path_file_string_dict,filter=10)

    number_of_spot_colors = len(string_list)

    return(number_of_spot_colors)

def _string_count_courses(path_file_string_dict):
    """returns the number of courses"""
    #gets the list of all strings with the filterd typ
    string_list = _input_2_filterd_string_list(path_file_string_dict,filter=2)

    number_of_courses = len(string_list)
    return(number_of_courses)

def _string_count_classes(path_file_string_dict):
    """returns the number of cs classes"""
    #gets the list of all strings with the filterd typ
    string_list = _input_2_filterd_string_list(path_file_string_dict,filter=3)

    number_of_classes = len(string_list)
    return(number_of_classes)

def _string_count_backgroundmaps(path_file_string_dict):
    """returns the number of backgroundmaps"""
    #gets the list of all strings with the filterd typ
    string_list = _input_2_filterd_string_list(path_file_string_dict,filter=8)

    number_of_backgroundmaps = len(string_list)
    return(number_of_backgroundmaps)

def _string_epsg_code(path_file_string_dict):
    """returns EPSG-Code, if map is georeferenced"""
    #gets the list of all strings with the filterd typ
    string_list = _input_2_filterd_string_list(path_file_string_dict,filter=1039)
    try:
        string_dict = _string_dict(string_list[0])
        epsg_code = ocad_grid_id_2_epsg[int(string_dict["i"])]["epsg"]
    except:
        epsg_code = None
    return(epsg_code)

def _string_epsg_name(path_file_string_dict):
    """returns EPSG-Name, if map is georeferenced"""
    #gets the list of all strings with the filterd typ
    string_list = _input_2_filterd_string_list(path_file_string_dict,filter=1039)
    try:
        string_dict = _string_dict(string_list[0])
        epsg_name = ocad_grid_id_2_epsg[int(string_dict["i"])]["name"]
    except:
        epsg_name = None
    return(epsg_name)

def _string_scale(path_file_string_dict):
    """returns scale of map"""
    #gets the list of all strings with the filterd typ
    string_list = _input_2_filterd_string_list(path_file_string_dict,filter=1039)
    try:
        string_dict = _string_dict(string_list[0])
        scale = string_dict["m"]
    except:
        scale = None
    return(scale)

def _string_georeferenced(path_file_string_dict):
    """returns True if map is georefferenced"""
    #gets the list of all strings with the filterd typ
    string_list = _input_2_filterd_string_list(path_file_string_dict,filter=1039)
    try:
        string_dict = _string_dict(string_list[0])
        georeferenced = _boolean(string_dict["r"])
    except:
        georeferenced = False
    return(georeferenced)

def _string_colors(path_file_string_dict):
    """returns a dict with all colors"""
    #gets the list of all strings with the filterd typ
    string_list = _input_2_filterd_string_list(path_file_string_dict,filter=9)
    colors_dict= {}
    for string in string_list:
        string_dict = _string_dict(string)
        colors_dict[int(string_dict["n"])]={"name": string_dict["First"],
        "cyan": int(string_dict["c"]),"magenta": int(string_dict["m"]),"yellow": int(string_dict["y"]),
        "black": int(string_dict["k"]), "overprint": _boolean(string_dict["o"]), "transparency": int(string_dict["t"])
        }


    return(colors_dict)


def _string_courses(path_file_string_dict):
    """returns a ?format? of all courses"""
    #gets the list of all strings with the filterd typ
    string_list = _input_2_filterd_string_list(path_file_string_dict,filter=2)
    courses_list= []
    for string in string_list:
        string_dict = _string_dict(string)


    return("?")



#==============================================================================
# Indexblock Things
#==============================================================================

def _get_index_blocks(path_file,*, type="string"):
    """returns a list with the position of all index blocks of the selected typ"""
    #if path given, opens the file, check if it is ocad
    file, file_close = _input_2_file_object(path_file)

    index_block_list = []
    if type == "string":
        file.seek(32)
    elif type == "object":
        pass
    elif type == "symbol":
        pass
    next_index_block = _int_rhex(file.read(4)) #this is actually the first
    while next_index_block > 0:
        index_block_list.append(next_index_block)
        file.seek(next_index_block)
        next_index_block = _int_rhex(file.read(4))

    #if file is opend in this function/ close it know
    if file_close: file.close()
    return(index_block_list)

def _get_ocad_strings(path_file,*,filter=None, output_typ="list"):
    """returns a list with all ocad strings, and the possibility to filter

    Parameter:
    filter = filter the string class
    output = list returns a list, dict returns a dict with {string-typ-id: string list}
    """
    #if path given, opens the file, check if it is ocad
    file, file_close = _input_2_file_object(path_file)

    index_block_list = _get_index_blocks(file, type="string")

    if output_typ == "list":
        output = []
    elif output_typ == "dict":
        output = {}

    for index_block in index_block_list:
        for i in range(0,256):
            file.seek(index_block+4+i*16)
            pos = _int_rhex(file.read(4))
            length = _int_rhex(file.read(4))
            rectype = _int_rhex(file.read(4))
            objindex = _int_rhex(file.read(4))
            if (filter == None or filter == rectype) and rectype != 0:
                file.seek(pos)
                string = file.read(length).decode("utf-8", errors='ignore')
                string=string.strip("\x00")
                if output_typ == "list":
                    output.append(string)
                elif output_typ == "dict":
                    if rectype not in output.keys():
                        output[rectype] = []
                    output[rectype].append(string)


    #if file is opend in this function/ close it know
    if file_close: file.close()
    return(output)
