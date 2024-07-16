import numpy as np
import matplotlib.pyplot as plt
import os.path
from matplotlib import _rc_params_in_file # type: ignore
from pathlib import Path
mplstyle = ['./style/no-latex.mplstyle',
            './style/my.mplstyle']

print(f'Draw filled contours from xpm file by gmx densmap.\n'
      f'Version 1.0, release date: 2024-Jun-25\n'
      f'Programmed by Jian Zhang (jian_zhang@cug.edu.cn)\n'
)
class XPM:
    def __init__(self, filename):
        self.filename = filename
        self.parse()

    
    def parse(self):
        with open(self.filename, encoding='utf-8') as xpm:
            while True:
                line = xpm.readline()
                
                # 提取legend
                if self.uncomment(line).strip().startswith('legend:'):
                    self.legend = self.uncomment(line).strip().split(':')[-1]

                # 提取x-label
                if self.uncomment(line).strip().startswith('x-label:'):
                    self.x_label = self.uncomment(line).strip().split(':')[-1]

                # 提取y-label
                if self.uncomment(line).strip().startswith('y-label:'):
                    self.y_label = self.uncomment(line).strip().split(':')[-1]

                if line.strip().startswith('static char *gromacs_xpm[]'):
                    break
            dim = xpm.readline()
            nx, ny, nc, nb = [int(i) for i in dim.strip().split('"')[1].split()]
            color = dict()
            for _ in range(nc):
                ls = xpm.readline().strip().split('"')
                color[ls[1][0]] = eval(ls[3])
            # 下面开始读取坐标轴数据
            data = np.zeros((int(nx / nb), ny))
            """
            每一列中为颜色的十六进制,即把<Pixels>字段换成颜色的十六进制
            """
            xval = []
            yval = []
            line = xpm.readline()
            while not line.strip().startswith('"'):
                s = self.uncomment(line).strip()
                if s.startswith('x-axis:'):
                    xval.extend([float(x) for x in s.strip('x-axis:  ').split()])
                elif s.startswith('y-axis:'):
                    yval.extend([float(x) for x in s.strip('y-axis:  ').split()])
                line = xpm.readline()
            for iy in range(ny):
                data[:, iy] = [color[self.unquote(line)[k:k+nb]] for k in range(0, nx, nb)]
                line = xpm.readline()
            # 把data反向
            self.array = data[:,::-1]
            if len(xval) > nx:
                xval.pop()
                yval.pop()
            self.xvalues = np.array(xval)
            self.yvalues = np.array(yval)


    @staticmethod
    def uncomment(s):
        # 去除/*与*/
        return s[2+s.find("/*") : s.rfind('*/')]
    

    @staticmethod
    def unquote(s):
        # 去除左右两侧的"
        return s[1+s.find('"') : s.rfind('"')]

file_path = None
while True:
    file_path = input('Please enter the path to your xpm file\n')
    if os.path.isfile(file_path):
        break

XPM_object = XPM(file_path)
x_label_str = XPM_object.x_label.split('"')[1]
y_label_str = XPM_object.y_label.split('"')[1]
legend_str = XPM_object.legend
cmap = 'jet'
alpha = 1
min_value = np.min(XPM_object.array)
max_value = np.max(XPM_object.array)
num_color_colorbar = 100
coor_scle_bool = False
dpi = 300
label_colorbar = 'Density'
color_scle_bool = False

while True:
    print(f' 0  x_label: {x_label_str}')
    print(f' 1  y_label: {y_label_str}')
    print(f' 2  style of colorbar: {cmap}')
    print(f' 3  alpha: {alpha}')
    print(f' 4  the number of color in colorbar: {str(num_color_colorbar)}')
    print(f' 5  Whether to turn on coordinate scale: {str(coor_scle_bool)}')
    print(f' 6  dpi: {str(dpi)}')
    print(f' 7  style file: {', '.join(mplstyle)}')
    print(f' 8  the label of colorbar: {label_colorbar}')
    print(f' 9  Whether to display the color bar scale: {color_scle_bool}')
    print(f'10  the range of values: ({min_value}, {max_value})')
    print(f' d  start to draw')
    
    
    match input():
        case '0':
            x_label_str = input('Please enter label of x axis.\n')
        case '1':
            y_label_str = input('Please enter label of y axis.\n')
        case '2':
            cmap = input('Please enter style of colorbar. Refer to: https://matplotlib.org/stable/users/explain/colors/colormaps.html\n')
        case '3':
            alpha = eval(input('Please enter alpha(0,1).\n'))
        case '4':
            num_color_colorbar = eval(input('Please enter the number of color in colorbar.\n'))
        case '5':
            coor_scle_bool = not coor_scle_bool
        case '6':
            dpi = int(input('Please enter dpi.\n'))
        case '7':
            mplstyle.append(input('Please the path of style file.\n'))
        case '8':
            label_colorbar = input('Please enter label of colorbar.\n')
        case '9':
            color_scle_bool = not color_scle_bool
        case '10':
            min_val_input = eval(input("Please enter the minimum value.\n"))
            max_val_input = eval(input("Please enter the minimum value.\n"))
            if max_val_input > min_val_input:
                min_value = min_val_input
                max_value = max_val_input
            else:
                print('Invalid range of values. Use default value.')
        case 'd':
            break
        case _:
            print('Invalid value. Use default value.')

print('Analyzing data...')

styles = {}
for path in mplstyle:
    path = Path(path)
    if path.is_file():
        styles[path.stem] = _rc_params_in_file(path)
        plt.style.core.update_nested_dict(plt.style.library, styles) # type: ignore
        plt.style.core.available[:] = sorted(plt.style.library.keys())
plt.style.use(list(styles.keys()))

X, Y = np.meshgrid(XPM_object.xvalues, XPM_object.yvalues)
Z = XPM_object.array
h = plt.contourf(X, Y, Z.transpose(), np.linspace(min_value, max_value, num_color_colorbar),cmap=cmap, alpha=alpha)
if coor_scle_bool:
    h.axes.set_xlabel(x_label_str)
    h.axes.set_ylabel(y_label_str)
else:
    h.axes.axis('off')
cbar = plt.colorbar(h)
# cbar.ax.set_xticks([])
if not color_scle_bool:
    cbar.ax.set_yticks([min_value, max_value], labels=['Low', 'High'])
    cbar.ax.tick_params(right=False)
cbar.set_label(label_colorbar)
plt.savefig('./XPM_draw.png', dpi=dpi)
plt.show()



