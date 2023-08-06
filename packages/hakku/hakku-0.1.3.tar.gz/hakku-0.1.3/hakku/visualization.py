import sys
import numpy as np
import pkg_resources as pkgr


def make_newick(tree_dir, _r=True):
    """
    Generate newick recursively from dict tree

    _r is recursion parameter, which should be ignored
    """

    if len(tree_dir) <= 0:
        # empty tree
        return ""

    s = "("
    comma = ""
    # loop cluster ids as node names
    for key in tree_dir.keys():
        # generate newick for subtree
        r = make_newick(tree_dir[key][0], _r=False)
        # add subtree and node name
        s += comma + r + str(key)
        comma = ","

    s += ")"

    # if it is level 1, add semicolon
    # to end newick tree
    if _r:
        s += ";"

    return s


def visualize(filename, delimiter='\t'):
    try:
        from ete3 import Tree, TreeStyle, TextFace
    except ImportError:
        print("ete3 not found, install with extras to use visualization")
        return

    # first line of the csv is header so skip it
    headerread = False

    # dir for tree structure
    ctree = {}

    with open(filename, 'r') as f:
        for line in f:
            if not headerread:
                # skip header
                headerread = True
            else:
                split = line.split(delimiter)

                # cluster ids
                first = split[0]
                clusters = first.split()

                # citation count
                cit = float(split[8])

                # cluster names
                names = [""]
                names += split[1:5]

                t = ctree

                # traverse the tree with the ids
                # add any nodes that are missing
                for i in range(len(clusters)):
                    # get cluster
                    k = clusters[i]
                    if k in t:
                        # cluster id in tree, add count
                        t[k] = (t[k][0], t[k][1]+1, t[k][2]+cit, names[i])
                    else:
                        # cluster missing from tree, add new node
                        t[k] = ({}, 1, cit, names[i])
                    # move to next node
                    t = t[k][0]

    # get newick string and create tree object
    # use format = 1 to keep node names
    tree_str = make_newick(ctree)
    tree = Tree(tree_str, format=1)

    # find size of biggest article cluster
    largest_cluster = ctree[list(ctree.keys())[0]][1]
    # find number of citations in the most cited cluster
    citmax = ctree[list(ctree.keys())[0]][2]
    if citmax < 1:
        citmax = 1

    # scale parameter to size cluster representation circles
    scale = 200 / np.sqrt(largest_cluster / np.pi)

    # get colormap for citation coloring
    viridis = np.load(pkgr.resource_filename("hakku", "viridis.npy"))

    # node layout func
    def my_layout(node):
        # get the node cluster ids from node names
        ks = list(reversed([n.name for n in node.get_ancestors()]))[1:]

        # visulization root node name is "", skip it
        if node.name:
            # cluster id list doesnt contain
            # current nodes name
            ks.append(node.name)

            # cluster size
            c_size = 0
            # citation count
            c_cit = 0
            # cluster name
            c_name = ""

            # get current nodes size and cit count
            # with cluster id list
            c = ctree
            for key in ks:
                c_size = c[key][1]
                c_cit = c[key][2]
                c_name = c[key][3]
                c = c[key][0]

            # use circle to represent cluster size
            node.img_style["shape"] = "circle"
            # circle area represents size
            circle_size = scale * np.sqrt(c_size / np.pi)
            node.img_style["size"] = circle_size

            # color with total citation count
            col = get_from_colormap(viridis, c_cit / citmax)
            node.img_style["fgcolor"] = color_to_hex(
                int(255*col[0]),
                int(255*col[1]),
                int(255*col[2]))

            # cluster size as number inside the circle
            fsize = 18
            # if circle is small use small font
            if circle_size < fsize * 2:
                fsize = 11
            f1 = TextFace(str(c_size), fsize=fsize, fgcolor="white", bold=True)
            # move text to center of the circle
            f1.margin_left = -circle_size / 2. \
                - f1.get_bounding_rect().width() / 2.
            node.add_face(f1, 0, position="branch-right")

            # show cluster ids
            f2 = TextFace(" ".join(ks))
            node.add_face(f2, 0, position="branch-bottom")

            # show cluster name
            f3 = TextFace(c_name)
            node.add_face(f3, 0, position="branch-top")

    # set tree style with custom layout
    s = TreeStyle()
    s.layout_fn = my_layout
    s.show_leaf_name = False
    # add extra space
    s.branch_vertical_margin = 10
    tree.show(tree_style=s)


def color_to_hex(r, g, b):
    return "#" + hex(
        (b % 256) * 256**0
        + (g % 256) * 256**1
        + (r % 256) * 256**2)[2:]


def get_from_colormap(cmap, val):
    return cmap[int((len(cmap)-1) * val)]


if __name__ == "__main__":
    if len(sys.argv) > 2:
        visualize(sys.argv[1], delimiter=sys.argv[2])
    else:
        visualize(sys.argv[1])
