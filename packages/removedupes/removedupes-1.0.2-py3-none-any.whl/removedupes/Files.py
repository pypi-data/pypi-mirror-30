import os, hashlib

class Files:
  def __init__(self, directory):
    self.directory = directory
    self.paths = Files.get_path_to_files(directory)

  @staticmethod
  def get_path_to_files(directory):
    files = []
    for filename in os.listdir(directory):
      path_to_file = os.path.join(directory, filename)
      if os.path.isfile(path_to_file):
        files.append(path_to_file)
    return files

  @staticmethod
  def group_by_file_size(file_paths):

    groups = {}

    for file_path in file_paths:
      file_size = os.path.getsize(file_path)

      if file_size in groups:
        groups[file_size].append(file_path)
      else:
        groups[file_size] = [file_path]

    return groups.values()

  @staticmethod
  def get_files_with_same_hash(file_groups, hash = hashlib.sha1, chunk_size = 1024, n_chunks = -1):

    hash_groups = {}

    for file_group in file_groups:
      if len(file_group) > 1:

        for file_path in file_group:

          hashobj = hash()

          with open(file_path, 'rb') as f:
            for i, chunk in enumerate(iter(lambda: f.read(4096), b'')):
                hashobj.update(chunk)
                if n_chunks > 0 and (i+1) >= n_chunks:
                  break

          _hash = hashobj.digest()

          if _hash in hash_groups:
            hash_groups[_hash].append(file_path)
          else:
            hash_groups[_hash] = [file_path]

    return hash_groups.values()

  def get_duplicates(self):
    file_groups = Files.group_by_file_size(self.paths)
    file_groups = Files.get_files_with_same_hash(file_groups, n_chunks=1)
    file_groups = Files.get_files_with_same_hash(file_groups)
    duplicate_files = [g[1:] for g in file_groups]
    return sum(duplicate_files, [])

  def removeDuplicates(self):
    duplicate_files = self.get_duplicates()

    for f in duplicate_files:
      os.remove(f)
    print('removed: {} files!'.format(len(duplicate_files)))
