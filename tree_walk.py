#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import argparse
import shutil
import hashlib


class FileSync():

    def _recurse(self, parent_path, file_list, sync_path):

        self._deleted(file_list, sync_path)

        if len(file_list) == 0:
            return

        if not os.path.exists(sync_path):
            print("NEW FOLDER: ", sync_path)
            os.mkdir(sync_path)

        for sub_path in file_list:
            full_path = os.path.join(parent_path, sub_path)

            if os.path.isdir(full_path):

                sync_full_path = os.path.join(sync_path, sub_path)

                if not os.path.exists(sync_full_path):
                    print("NEW FOLDER: ", sync_full_path)
                    os.mkdir(sync_full_path)

                self._recurse(full_path, os.listdir(full_path), sync_full_path)

            elif os.path.isfile(full_path):

                filename = full_path.split(os.path.sep)
                sync_file = os.path.join(sync_path, filename[-1])

                if not (os.path.exists(sync_file)):
                    shutil.copy2(full_path, sync_path)
                    print("NEW FILE: ", sync_file)

                elif not self._check_md5(full_path, sync_file):
                    shutil.copy2(full_path, sync_path)
                    print("UPDATE FILE: ", sync_file)

    def _check_md5(self, input_file, output_file):
        with open(input_file, "r", encoding="utf-8", errors="ignore") as in_file, \
                open(output_file, "r", encoding="utf-8", errors="ignore") as out_file:

            md5_input = hashlib.md5(in_file.read().encode()).hexdigest()
            md5_output = hashlib.md5(out_file.read().encode()).hexdigest()
            return md5_input == md5_output

    def _delete_recurse(self, folder, subdirs):
        if len(subdirs) == 0:
            os.rmdir(folder)
            print("DELETED FOLDER", folder)
            return

        for file in subdirs:
            full_path = os.path.join(folder, file)

            if os.path.isdir(full_path):
                self._delete_recurse(full_path, os.listdir(full_path))
                if os.path.exists(full_path):
                    os.rmdir(full_path)
                    print("DELETED FOLDER", full_path)
            else:
                os.remove(full_path)
                print("DELETED FILE", full_path)

    def _deleted(self, file_list, sync_path):
        src_files = set(file_list)

        if os.path.isdir(sync_path):
            dst_files = set(os.listdir(sync_path))
        else:
            return 

        deleted_files = dst_files.difference(src_files)

        if len(deleted_files) > 0:
            for file in deleted_files:
                full_path = os.path.join(sync_path, file)

                if os.path.isdir(full_path):
                    self._delete_recurse(full_path, os.listdir(full_path))
                else:
                    os.remove(full_path)
                    print("DELETE FILE: ", full_path)

    def sync(self, args):
        self.src = args.source
        self.dst = args.destination

        if not os.path.isdir(self.dst):
            os.mkdir(self.dst)
            
        self._recurse(self.src, os.listdir(self.src), self.dst)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-src", "--source",
                        help="Original folder", default=".")
    parser.add_argument("-dst", "--destination",
                        help="Destination folder", default="../folderSync")

    args = parser.parse_args()
    FileSync().sync(args)
