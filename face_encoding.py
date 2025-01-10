import face_recognition as fc

class Face_Encoding:
    def __init__(self, name:str):
        self._name = name
        self._know_face_encoding = []

    def check_img(self, img) -> bool:
        if len(img.split(".")) != 2: raise TypeError("This need to be an image file")
        file_extension = img.split(".")[-1]
        file_ext_name = {'jpg', 'jpeg', 'png', 'bmp', 'tiff', 'gif'}
        if file_extension not in file_ext_name:
            raise TypeError('Program does not support this type of image format')
        return True
    
    def get_face_encoding(self, img: str) -> None:
        try:
            reference_img = fc.load_image_file(img)
            if reference_img is None or reference_img.size == 0:
                print(f"Couldn't load {img}")
                raise ValueError("Couldn't load img")
            else:
                encoding = fc.face_encodings(reference_img)[0]
                self._know_face_encoding.append(encoding)
        except IndexError:
            with open('Error_img.txt', 'a') as file:
                file.write(f"Couldn't read/encoing {img}")
        except Exception as e:
            print(f"An Exception was found with {img}: {e}")
    
    def add_known_faces(self, img:str) -> None:
        if self.check_img(img):
            self.get_face_encoding(img)
    
    def get_encodings(self) -> list:
        return self._know_face_encoding
    
    def train_with_mult_imgs(self, imgs: list) -> None:
        for img in imgs:
            self.add_known_faces(img)
    
    def get_name(self) -> str: return self._name