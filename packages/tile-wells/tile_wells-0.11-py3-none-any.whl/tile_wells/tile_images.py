import matplotlib.pyplot as plt

def tile_images(img_dir, channel, input_format, output_format, timestamp_dir):
    '''Layout the well images in a grid representing the multiwell plate'''
    print(channel)
    # Prevent figure windows from showing up
    plt.ioff()
    img_names = sorted(list(img_dir.glob('{}-*.{}'.format(channel, input_format))))
    rows = set([img.name[2] for img in img_names])
    cols = set([int(img.name[3:5]) for img in img_names])
    fig, axes = plt.subplots(len(rows), len(cols), figsize=(len(cols)*4, len(rows)*4))
    for ax, img_name in zip(axes.ravel(), img_names):
        print(img_name.name)
        ax.axis('off')
        ax.imshow(plt.imread(img_name), cmap='gray', vmin=0, vmax=256)
#         ax.set_title(img_name.name, fontsize=20, color='white', y=0.5)
#     fig.tight_layout(pad=20, w_pad=50, h_pad=50, rect=[0, 0, 0.992, 0.993])
    fig.tight_layout(pad=0, w_pad=-3, h_pad=-2, rect=[0, 0, 0.992, 0.993])
    # Pyplot can't handle Path object yet, lands in 2.1
    # https://github.com/matplotlib/matplotlib/pull/8481
    print('Saving image...')
    fig.savefig(timestamp_dir.joinpath('ch{}.{}'.format(
        channel, output_format)).as_posix(), dpi=200)#, bbox_inches='tight', pad_inches=0)
    return None


