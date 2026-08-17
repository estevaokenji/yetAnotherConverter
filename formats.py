class Format:
    def __init_subclass__(cls):
        cls.name = cls.__name__
        cls.extension = cls.__name__.lower()
    modes = ("RGB", "L")
    animated = False

class PNG(Format):
    modes = ("RGBA", "RGB", "LA", "L", "P", "1")
    animated = True

class JPEG(Format):
    extension = "jpg"
    modes = ("RGB","L")

class WEBP(Format):
    modes = ("RGB", "RGBA", "L", "LA")
    animated = True

class GIF(Format):
    modes = ("P",)
    animated = True

class BMP(Format):
    modes = ("RGB", "L", "P", "1")

class TIFF(Format):
    modes = ("RGBA", "RGB", "LA", "L", "P", "1")

class ICO(Format):
    modes = ("RGBA", "RGB", "L", "P", "1")

class PPM(Format):
    modes = ("RGB",)

class TGA(Format):
    modes = ("RGBA", "RGB", "L", "P")