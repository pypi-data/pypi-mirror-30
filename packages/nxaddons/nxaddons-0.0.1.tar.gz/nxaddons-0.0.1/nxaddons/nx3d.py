def draw_nxgraph3D(G, pos=None, figtitle=None, ax=None):
    #pos is an Nx3 array (3D positions of nodes)
    #layout is a dict with node keys and pos-vector(3D) values
    import numpy as np
    if pos is None:
        #generate some layout
        import networkx as nx
        layout = nx.spring_layout(G, dim=3)
        pos = np.array([layout[i] for i in sorted(G.nodes())])
    if pos.shape[1]==2:
        #Add zcol to pos
        pos=np.c_[ pos, np.ones(pos.shape[0]) ] 
    
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D

    #Setting up figure
    if ax is None:
        fig = plt.figure(figsize=(9,6))
        ax = fig.add_subplot(1, 1, 1, projection='3d')
        if figtitle: 
            fig.suptitle(figtitle)
        else:
            fig.suptitle('Graph3D n={} e={}'.format(len(G.nodes()), len(G.edges())))
    else:
        fig = ax.get_figure()
    
    #Draw graph
    ax.scatter(xs=pos[:,0],ys=pos[:,1],zs=pos[:,2], s=22, c='red')
    def getEmptyEdgelines(n):
        i = 0
        while i < n:
            # ax.plot3D([],[],[]) returns list with one line3D element. 
            # yeild the line3D element. 
            yield ax.plot([], [], [], '-', c='black', linewidth=0.5)[0]
            i += 1
    edgelines = getEmptyEdgelines(len(G.edges()))
    for edge, edgeline in zip(G.edges(),edgelines):
        a,b = edge
        xs,ys,zs=pos[:,0],pos[:,1],pos[:,2]
        edgeline.set_data([xs[a], xs[b]],[ys[a], ys[b]] )
        edgeline.set_3d_properties([zs[a],zs[b]])

    #plt.savefig(exportDir+'time-evolution-hd.svg', dpi=256);
    #plt.show()
    
    return fig,ax