#!/usr/bin/env python

import sys, os
from subprocess import call
from os.path import expanduser

def comments():
    CSI = '\033['
    print CSI + "31;32m" + u'Example to run:' + CSI + "0m"
    print CSI + "31;32m" + u' - dedepuyer -r beta\n - dedepuyer -r stable\n - dedepuyer -r preview' + CSI + "0m"

def make_executable(path):
    mode = os.stat(path).st_mode
    mode |= (mode & 0o444) >> 2    # copy R bits to X
    os.chmod(path, mode)

def main():
    try:
        options = sys.argv[1]
        arg = sys.argv[2]
        if options == '--help':
            comments()
        else:
            if options == '-r' and (arg == 'stable' or arg == 'beta' or arg == 'preview'):
								commands = """
#!/bin/bash -e

readonly BETA=0
readonly STABLE=1
readonly PREVIEW=2

generate_version() {
	format="v$(date +%Y%m%d.%s)"

	case "$1" in
		0)
			version="beta-$format"
		;;
		1)
			version="stable-$format"
		;;
		2)
			version="preview-$format"
		;;
	esac

	echo "Version $version generated."
}

create_tag() {
	echo "Please input tag description:"
	read tag_description
	echo Tag description: $tag_description

	git tag -a $version -m "$tag_description"
}

push_tag() {
	echo "Pushing version $version to repository..."

	git push origin $version

	echo "Tag $version succesfully pushed to repository."
}

release_version() {
	echo "Releasing version $version..."

	generate_version $1
	create_tag
	push_tag

	echo "Version release completed."
}

while getopts "r:" option; do
	case "${option}" in
		r)
			release_type=${OPTARG}

			case "$release_type" in
				beta)
					release_version $BETA
				;;
				stable)
					release_version $STABLE
				;;
				preview)
					release_version $PREVIEW
				;;
			esac
		;;
	esac
done
													 """
								path = expanduser("~") + "/dedepuyer" 
								file = open( path ,"w")
								file.write(commands)
								file.close()
								
								make_executable(path)
								call(path + " '%s' '%s'" % (options,arg), shell=True)
            else:
                CSI = "\x1B["
                print CSI + "31;40m" + u"Argument is not valid: Run with --help" + CSI + "0m"
    except Exception as e:
        print e
        comments()
        sys.exit(1)

main()
