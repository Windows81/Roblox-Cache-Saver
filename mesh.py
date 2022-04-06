import os
from pip import List
import struct
import io
import argparse


class mesh_v1:
    class VertexContainer:
        px: float
        py: float
        pz: float  # position
        nx: float
        ny: float
        nz: float  # normal
        tu: float
        tv: float
        tw: float  # uv (v is 1.0 - v, w is unused (0))

    class FaceContainer:
        v1: int
        v2: int
        v3: int

    class Tuple:
        a: float
        b: float
        c: float


class mesh_v2:
    class MeshHeader:
        sizeof_MeshHeader: int
        sizeof_Vertex: int
        sizeof_Face: int

        numVerts: int
        numFaces: int

    class Vertex:
        px: float
        py: float
        pz: float  # position
        nx: float
        ny: float
        nz: float  # unit normal
        tu: float
        tv: float
        tx: float  # uv coords
        ty: float
        tz: float
        ts: float
        r: int
        g: int
        b: int
        a: int  # colour

    class Face:
        a: int
        b: int
        c: int


def convert(inputFile: io.BufferedReader, outputFile: io.BufferedWriter) -> bool:
    # https://devforum.roblox.com/t/roblox-mesh-format/326114

    word = inputFile.read(8)
    if word != b"version ":
        print("Not a ROBLOX .mesh file!")
        return False
    version = inputFile.read(5)

    if version == b"1.00\n" or version == b"1.01\n":
        scale = 0.5 if version == b"1.00\n" else 1.0
        strNumFaces = inputFile.readline()

        numFaces = int(strNumFaces)
        numVerts = numFaces * 3
        numTuples = numVerts * 3

        # Read tuples.
        tuples = []

        currTuple = (0, 0)
        n_currTuple = 0
        i_currTuple = 0
        currByte = bytes([0])
        tupleVal = bytes()

        while inputFile.tell():
            currByte = inputFile.read(1)

            if currByte == b"]":
                v_currTuple = mesh_v1.Tuple()
                v_currTuple.a = currTuple[0]
                v_currTuple.b = currTuple[1]
                v_currTuple.c = float(tupleVal)
                tuples[n_currTuple] = v_currTuple
                n_currTuple += 1
                i_currTuple = 0
                tupleVal = bytes()
                continue

            elif currByte == b"[":
                continue

            elif currByte == b",":
                currTuple[i_currTuple] = float(tupleVal)
                tupleVal = bytes()
                i_currTuple += 1
                continue

            else:
                tupleVal += currByte

        # Output.
        vertices = numVerts * [None]
        for i in range(0, numTuples, 3):
            face = tuples + i
            vtx = mesh_v1.VertexContainer()

            vtx.px = face[0].a * scale
            vtx.py = face[0].b * scale
            vtx.pz = face[0].c * scale

            vtx.nx = face[1].a
            vtx.nx = face[1].b
            vtx.nz = face[1].c

            vtx.tu = face[2].a
            vtx.tv = face[2].b
            vtx.tw = 0.0

            vertices[i / 3] = vtx

        outputFile.write(bytes(f"# ROBLOX .mesh version 1.0 (scale = {scale})\n"))

        # Write vertex position data.
        for v in vertices:
            outputFile.write(bytes(f"v {v.px} {v.py} {v.pz}\n", "UTF-8"))

        # Write vertex UV data.
        for i in range(0, numVerts):
            outputFile.write(bytes(f"vt {v.tu} {v.tv}\n", "UTF-8"))

        # Write vertex normal data.
        for i in range(0, numVerts):
            outputFile.write(bytes(f"vn {v.nx} {v.ny} {v.nz}\n", "UTF-8"))

        outputFile.write(b"s 1\n")

        # Write faces.
        for i in range(1, numVerts + 1, 3):
            outputFile.write(bytes(f"f {i}/{i}/{i} ", "UTF-8"))
            i += 1
            outputFile.write(bytes(f"{i}/{i}/{i} ", "UTF-8"))
            i += 1
            outputFile.write(bytes(f"{i}/{i}/{i}\n", "UTF-8"))
        return True

    if version == b"2.00\n":

        # One short, two unsigned chars, two unsigned ints.
        header_f = "HBBII"

        # Three unsigned ints.
        face_f = "III"

        header = mesh_v2.MeshHeader()
        header_s = struct.calcsize(header_f)
        (
            header.sizeof_MeshHeader,
            header.sizeof_Vertex,
            header.sizeof_Face,
            header.numVerts,
            header.numFaces,
        ) = struct.unpack(header_f, inputFile.read(header_s))

        if header.sizeof_MeshHeader != header_s:
            print("ERROR: Mesh header size invalid.")
            return False

        vertices: List[mesh_v2.Vertex] = header.numVerts * [None]
        faces: List[mesh_v2.Face] = header.numFaces * [None]

        vertex_f = {
            # Eight floats, four signed bytes, four unsigned bytes.
            40: "ffffffffbbbbBBBB",
            # Eight floats, four signed bytes.
            36: "ffffffffbbbb",
        }.get(header.sizeof_Vertex)

        # Read vertex array
        for i in range(0, len(vertices)):
            v = vertices[i] = mesh_v2.Vertex()
            a = struct.unpack(vertex_f, inputFile.read(header.sizeof_Vertex))
            if header.sizeof_Vertex == 36:
                a += (255, 255, 255, 255)
            (
                v.px,
                v.py,
                v.pz,
            ) = a[0:3]
            (
                v.nx,
                v.ny,
                v.nz,
            ) = a[3:6]
            (
                v.tu,
                v.tv,
                v.tx,
                v.ty,
                v.tz,
                v.ts,
            ) = a[6:12]
            (
                v.r,
                v.g,
                v.b,
                v.a,
            ) = a[12:16]

        # Read face array
        for i in range(0, len(faces)):
            f = faces[i] = mesh_v2.Face()
            f.a, f.b, f.c = struct.unpack(face_f, inputFile.read(header.sizeof_Face))
            f.a += 1
            f.b += 1
            f.c += 1

        # Output.
        outputFile.write(b"# ROBLOX .mesh version 2.00.\n")

        # Write vertex position data.
        for v in vertices:
            outputFile.write(bytes(f"v {v.px} {v.py} {v.pz}\n", "UTF-8"))

        # Write vertex UV data.
        for i in range(0, header.numVerts):
            outputFile.write(bytes(f"vt {v.tu} {v.tv}\n", "UTF-8"))

        # Write vertex normal data.
        for i in range(0, header.numVerts):
            outputFile.write(bytes(f"vn {v.nx} {v.ny} {1.0-v.nz}\n", "UTF-8"))

        outputFile.write(b"s 1\n")

        # Write faces.
        for f in faces:
            outputFile.write(bytes(f"f {f.a}/{f.a}/{f.a} ", "UTF-8"))
            outputFile.write(bytes(f"{f.b}/{f.b}/{f.b} ", "UTF-8"))
            outputFile.write(bytes(f"{f.c}/{f.c}/{f.c}\n", "UTF-8"))
        return True

    print(f"ERROR: Unknown version {version}.")
    return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=os.path.abspath)
    parser.add_argument("output", type=os.path.abspath)
    args = parser.parse_args()

    i = open(args.input, "rb")
    o = open(args.output, "xb")
    s = convert(i, o)
    i.close()
    o.close()
    if not s:
        os.remove(args.output)
        exit(1)
