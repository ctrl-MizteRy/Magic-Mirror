from face_encoding import Face_Encoding
import os
import glob
import pickle

class Train_Faces:
    def __init__(self):
        self.people = {}

    def get_imgs_from_folder(self, path: str) -> list[str]:
        img_ext =  {'jpg', 'jpeg', 'png', 'bmp', 'tiff', 'gif'}
        img_files = []
        if not os.path.isdir(path):
            raise ValueError(f"The provide path: '{path}' is not correct.")
        for ext in img_ext:
            pattern = os.path.join(path, f"*.{ext}")
            img_files.extend(glob.glob(pattern))
        if len(img_files) == 0:
            raise ValueError('There is no img in this file.')
        return img_files

    def start_training(self, file_paths : list[str]) -> None:
        if len(file_paths) > 0 :
            for path in file_paths:
                person_name = os.path.basename(path)
                imgs = self.get_imgs_from_folder(path)
                if imgs:
                    person = Face_Encoding(person_name)
                    person.train_with_mult_imgs(imgs)
                    self.people[person_name] = person
    
    def get_people_encoding(self) -> dict[str, 'Face_Encoding']:
        return self.people
    
    def store_face_encoding(self, encode_file: str) -> None:
        try:
            with open(encode_file, 'wb') as file: #.pkl for pickle files
                pickle.dump(self.people, file)
        except Exception as e:
            print(f"Error copying the file: {e}")

    def load_face_encoding(self, encode_file: str) -> None:
        try:
            with open(encode_file, 'rb') as file:
                self.people = pickle.load(file)
        except FileNotFoundError:
            print(f"Couldn't not find the encoding file: {encode_file}")
        except Exception as e:
            print(f"Error loading the file: {e}")