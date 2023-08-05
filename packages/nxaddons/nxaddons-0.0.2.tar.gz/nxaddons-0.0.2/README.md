# nxaddons
Extended tools for NetworkX package

## Usage
	from nxaddons import nx3d

	G=nx3d.nx.hypercube_graph(4)
	fig1,ax1 = nx3d.draw_graph(G, pos=nx3d.np.random.random(size=(len(G),3)), figtitle='4D-Hypercube (Random-layout)')
	fig2,ax2 = nx3d.draw_graph(G, figtitle='4D-Hypercube (Spring-layout)', show=True)
	