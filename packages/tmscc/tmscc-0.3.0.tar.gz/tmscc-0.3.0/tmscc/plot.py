from sklearn.manifold import TSNE


def tsne(theta):
    tsne = TSNE(n_components=2).fit_transform(theta)
    plt.scatter(tsne[:, 0], tsne[:, 1])
