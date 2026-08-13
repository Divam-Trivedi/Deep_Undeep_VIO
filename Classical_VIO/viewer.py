import numpy as np
import OpenGL.GL as gl
import pypangolin as pangolin

import cv2

from multiprocessing import Queue, Process



class Viewer(object):
    def __init__(self):
        self.image_queue = Queue()
        self.pose_queue = Queue()

        self.view_thread = Process(target=self.view)
        self.view_thread.start()

    def update_pose(self, pose):
        if pose is None:
            return
        self.pose_queue.put(pose.matrix())

    def update_image(self, image):
        if image is None:
            return
        elif image.ndim == 2:
            image = np.repeat(image[..., np.newaxis], 3, axis=2)
        self.image_queue.put(image)
            

    def view(self):
        pangolin.CreateWindowAndBind('Viewer', 1024, 768)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc (gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

        viewpoint_x = 0
        viewpoint_y = -7  
        viewpoint_z = -30
        viewpoint_f = 1000

        W, H    = 1024, 768
        fx, fy  = viewpoint_f, viewpoint_f
        cx, cy  = 512,        389
        depth_z = 0.5         # how far out to draw the frustum

        proj = pangolin.ProjectionMatrix(
            1024, 768, fx, fy, 512, 389, 0.1, 300)
        look_view = pangolin.ModelViewLookAt(
            viewpoint_x, viewpoint_y, viewpoint_z, 0, 0, 0, 0, -1, 0)

        # Camera Render Object (for view / scene browsing)
        scam = pangolin.OpenGlRenderState(proj, look_view)

        # Add named OpenGL viewport to window and provide 3D Handler
        dcam = pangolin.CreateDisplay()
        # dcam.SetBounds(0.0, 1.0, 175 / 1024., 1.0, -1024 / 768.)
        dcam.SetBounds(
                        pangolin.Attach.Frac(0.0),           # bottom
                        pangolin.Attach.Frac(1.0),           # top
                        pangolin.Attach.Frac(175/1024.0),    # left
                        pangolin.Attach.Frac(1.0),            # right
                    )

        dcam.SetHandler(pangolin.Handler3D(scam))

        # image
        width, height = 376, 240
        dimg = pangolin.Display('image')
        # dimg.SetBounds(0, height / 768., 0.0, width / 1024., 1024 / 768.)
        dimg.SetBounds(
                        pangolin.Attach.Frac((H - height)/H),  # bottom = (768–240)/768
                        pangolin.Attach.Frac(1.0),             # top    = 768/768
                        pangolin.Attach.Frac(0.0),             # left   = 0/1024
                        pangolin.Attach.Frac(width/1024.0)     # right  = 376/1024
                    )

        # dimg.SetLock(pangolin.Lock.LockLeft, pangolin.Lock.LockTop)

        texture = pangolin.GlTexture(width, height, gl.GL_RGB, False, 0, gl.GL_RGB, gl.GL_UNSIGNED_BYTE)
        image = np.ones((height, width, 3), 'uint8')

        # axis
        # axis = pangolin.Renderable()
        # axis.Add(pangolin.Axis())

        def draw_axes(length=1.0):
            print("Drawing axes")
            gl.glLineWidth(2)
            gl.glBegin(gl.GL_LINES)
            # X‐axis in red
            gl.glColor3f(1.0, 0.0, 0.0)
            gl.glVertex3f(0.0, 0.0, 0.0)
            gl.glVertex3f(length, 0.0, 0.0)
            # Y‐axis in green
            gl.glColor3f(0.0, 1.0, 0.0)
            gl.glVertex3f(0.0, 0.0, 0.0)
            gl.glVertex3f(0.0, length, 0.0)
            # Z‐axis in blue
            gl.glColor3f(0.0, 0.0, 1.0)
            gl.glVertex3f(0.0, 0.0, 0.0)
            gl.glVertex3f(0.0, 0.0, length)
            gl.glEnd()
            # reset to white for other draws
            gl.glColor3f(1.0, 1.0, 1.0)



        trajectory = DynamicArray()
        camera = None
        image = None

        while not pangolin.ShouldQuit():
            if not self.pose_queue.empty():
                while not self.pose_queue.empty():
                    pose = self.pose_queue.get()
                trajectory.append(pose[:3, 3])
                camera = pose

            if not self.image_queue.empty():
                while not self.image_queue.empty():
                    img = self.image_queue.get()
                img = img[::-1, :, ::-1]
                img = cv2.resize(img, (width, height))
                image = img.copy()

            gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
            gl.glClearColor(1.0, 1.0, 1.0, 1.0)
            dcam.Activate(scam)


            # draw axis
            # axis.Render()
            draw_axes()

            # draw current camera
            # if camera is not None:
            #     gl.glLineWidth(1)
            #     gl.glColor3f(0.0, 0.0, 1.0)
            #     gl.glPushMatrix()
            #     gl.glMultMatrixf(camera.T.astype('float32').flatten())
            #     pangolin.glDrawFrustum(0.5)
            #     gl.glPopMatrix()
                # mv = pangolin.OpenGlMatrix()
                # mv.m = camera.flatten().tolist()
                # pangolin.glSetFrameOfReference(mv)
                # pangolin.glDrawFrustum(0.5)      # the argument is the scale/size of the pyramid
                # pangolin.glUnsetFrameOfReference()
                # pangolin.DrawCameras(np.array([camera]), 0.5)

            if camera is not None:
                gl.glColor3f(0.0, 0.0, 1.0)
                gl.glLineWidth(1)

                gl.glPushMatrix()
                # multiply in the camera‐to‐world pose
                # camera[:3,3] *= 0.01
                gl.glMultMatrixf(camera.T.astype('float32').flatten())

                # exactly these seven args:
                fx_cam, fy_cam = 320.0, 320.0      # e.g. ≈320 px focal length
                cx_cam, cy_cam = 188.0, 120.0      # e.g. center of 376×240 image
                w_cam,  h_cam  = 376,   240        # your image size
                z_draw = 0.005                       # draw near‐plane at 10 cm in front

                pangolin.glDrawFrustum(
                    fx_cam, fy_cam,
                    cx_cam, cy_cam,
                    w_cam,  h_cam,
                    z_draw
                )
                gl.glPopMatrix()

            # show trajectory
            pts = trajectory.array().astype('float32')  # (N,3)
            if pts.shape[0] > 0:
                gl.glColor3f(0.0, 0.0, 0.0)
                gl.glPointSize(2)
                # build the list of 3×1 vectors
                cols = [pts[i].reshape((3,1)) for i in range(pts.shape[0])]
                pangolin.glDrawPoints(cols)
                # pangolin.DrawPoints(trajectory.array())

            # show image
            if image is not None:
                texture.Upload(image, gl.GL_RGB, gl.GL_UNSIGNED_BYTE)
                dimg.Activate()
                gl.glColor3f(1.0, 1.0, 1.0)
                texture.RenderToViewport()
                
            pangolin.FinishFrame()




class DynamicArray(object):
    def __init__(self, shape=3):
        if isinstance(shape, int):
            shape = (shape,)
        assert isinstance(shape, tuple)

        self.data = np.zeros((1000, *shape))
        self.shape = shape
        self.ind = 0

    def clear(self):
        self.ind = 0

    def append(self, x):
        self.extend([x])
    
    def extend(self, xs):
        if len(xs) == 0:
            return
        assert np.array(xs[0]).shape == self.shape

        if self.ind + len(xs) >= len(self.data):
            self.data.resize(
                (2 * len(self.data), *self.shape) , refcheck=False)

        if isinstance(xs, np.ndarray):
            self.data[self.ind:self.ind+len(xs)] = xs
        else:
            for i, x in enumerate(xs):
                self.data[self.ind+i] = x
            self.ind += len(xs)

    def array(self):
        return self.data[:self.ind]

    def __len__(self):
        return self.ind

    def __getitem__(self, i):
        assert i < self.ind
        return self.data[i]

    def __iter__(self):
        for x in self.data[:self.ind]:
            yield x




if __name__ == '__main__':
    import g2o
    import time

    viewer = Viewer()
    viewer.update_pose(g2o.Isometry3d())


    # viewer.view_thread.join()