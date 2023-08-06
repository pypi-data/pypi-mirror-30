import sys
from mhelper import file_helper, markdown_helper


__version__ = "1.0.0.6"


def main():
    if len( sys.argv ) < 2:
        file_name = "readme.md"
    else:
        file_name = sys.argv[1]
    
    try:
        text = file_helper.read_all_text( file_name )
    except FileNotFoundError as ex:
        print( str( ex ) )
        return 2
    
    if not text:
        print( "File is missing or empty.", file = sys.stderr )
        return 3
    
    ansi = markdown_helper.markdown_to_ansi( text )
    
    print( ansi )
    return 0


if __name__ == "__main__":
    exit( main() )
