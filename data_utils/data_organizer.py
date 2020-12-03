import argparse
import glob
import os
import shutil


def do_2003_keys(in_dir, out_dir):
    dir_items = os.listdir(out_dir)
    dir_items = list(filter(lambda x: os.path.isdir(out_dir + os.path.sep + x), dir_items))
    dir_items = list(map(int, dir_items))
    dir_items.sort()
    dir_items = list(map(str, dir_items))
    for item in dir_items:
        print(item)
        item_full_path = out_dir + os.path.sep + item
        key_dir_path = item_full_path + os.path.sep + "keys"
        if not os.path.exists(key_dir_path):
            os.mkdir(key_dir_path)

        orig_dir_filename = item_full_path + os.path.sep + "original_dir_name.txt"
        with open(orig_dir_filename, 'r') as orig_dir_file:
            orig_dir_name = orig_dir_file.readlines()[0]

        orig_dir_name = format_docset_name(orig_dir_name)
        summary_file_path = in_dir + os.path.sep + orig_dir_name + "*"
        summary_files = glob.glob(summary_file_path)
        idx = 0
        for sfi in summary_files:
            if sfi.find(".100.") > -1:
                print(sfi + " -> " + str(idx))
                shutil.copy2(sfi, key_dir_path + os.path.sep + str(idx) + ".txt")
                with open(key_dir_path + os.path.sep + f"orig_key_name.{idx}.txt",
                          'w') as orig_key_name:
                    orig_key_name.write(sfi)
                idx += 1


def do_2003(in_dir, out_dir):
    """
    Grab all 60 documents, create a dir for each, along with their 4 human summaries
    :return:
    """

    dir_items = setup_outdir_and_get_input(in_dir, out_dir)
    for idx, item in enumerate(dir_items):
        full_path = in_dir + os.path.sep + item
        print(f"{item} -> {idx}")
        create_dirs_and_write_files(full_path, idx, in_dir, item, out_dir)


def do_2004_keys(in_dir, out_dir):
    do_2003_keys(in_dir, out_dir)


def do_2004(in_dir, out_dir):
    """
    Handle formatting the DUC 2004 documents
    :return: a directory containing and an easier to process data set
    """
    dir_items = setup_outdir_and_get_input(in_dir, out_dir)
    for idx, item in enumerate(dir_items):
        full_path = in_dir + os.path.sep + item
        print(f"{full_path} -> {out_dir}/{idx}")
        create_dirs_and_write_files(full_path, idx, in_dir, item, out_dir)


def format_docset_name(orig_dir_name):
    # capitalize the first character and remove the last
    orig_dir_name = list(orig_dir_name)
    orig_dir_name[0] = str(orig_dir_name[0]).capitalize()
    orig_dir_name = "".join(orig_dir_name)
    orig_dir_name = orig_dir_name[:-1]
    print(orig_dir_name)
    return orig_dir_name


def create_dirs_and_write_files(full_path, idx, in_dir, item, out_dir):
    full_out_path = out_dir + os.path.sep + str(idx)
    preserve_orig_dir_name(full_out_path, item)
    folder_items = get_folder_contents(in_dir, full_path)
    for jdx, f_item in enumerate(folder_items):
        print(f"{f_item} -> {jdx}.sgml")
        full_file_out_path = create_subfolder_preserve_old_filename(f_item, full_out_path, jdx)
        final_file_name = full_file_out_path + os.path.sep + str(jdx) + ".sgml"
        shutil.copy2(in_dir + os.path.sep + item + os.path.sep + f_item, final_file_name)


def create_subfolder_preserve_old_filename(f_item, full_out_path, jdx):
    full_file_out_path = full_out_path + os.path.sep + str(jdx)
    if not os.path.isdir(full_file_out_path):
        os.mkdir(full_file_out_path)
    with open(full_file_out_path + os.path.sep + "original_file_name.txt",
              'w') as orig_dir_name:
        print("Writing origFileName file...")
        orig_dir_name.write(f_item)
    return full_file_out_path


def get_folder_contents(in_dir, full_path):
    folder_items = os.listdir(full_path)
    folder_items = list(
        filter(lambda x: not os.path.isdir(in_dir + os.path.sep + x), folder_items)
    )
    folder_items.sort()
    return folder_items


def get_subfolders(full_path):
    folder_items = os.listdir(full_path)
    folder_items = list(
        filter(lambda x: os.path.isdir(full_path + os.path.sep + x), folder_items)
    )
    folder_items.sort()
    return folder_items


def preserve_orig_dir_name(full_out_path, item):
    if not os.path.isdir(full_out_path):
        os.mkdir(full_out_path)
    with open(full_out_path + os.path.sep + "original_dir_name.txt", 'w') as orig_dir_name:
        print("Writing orig_dir_name file...")
        orig_dir_name.write(item)


def setup_outdir_and_get_input(in_dir, out_dir):
    # check that out dir exists
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    dir_items = os.listdir(in_dir)
    dir_items = list(filter(lambda x: os.path.isdir(in_dir + os.path.sep + x), dir_items))
    dir_items.sort()
    return dir_items


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Format DUC Data.')
    parser.add_argument('in_data_directory', metavar='in', type=str,
                        help='The raw data directory')
    parser.add_argument('in_key_directory', metavar='keys', type=str,
                        help='The answer key directory')
    parser.add_argument('out_data_directory', metavar='out', type=str,
                        help='The output data directory')
    parser.add_argument('--2003', dest='is2003', action='store_true',
                        help='Format DUC 2003 Task 1 Data', default=False)
    parser.add_argument('--2004', dest='is2004', action='store_true',
                        help='Format DUC 2004 Task 2 Data', default=False)

    args = parser.parse_args()
    # print(args.in_data_directory)
    # print(args.out_data_directory)

    if args.is2003:
        do_2003(args.in_data_directory, args.out_data_directory)
        do_2003_keys(args.in_key_directory, args.out_data_directory)
    elif args.is2004:
        do_2004(args.in_data_directory, args.out_data_directory)
        do_2004_keys(args.in_key_directory, args.out_data_directory)
