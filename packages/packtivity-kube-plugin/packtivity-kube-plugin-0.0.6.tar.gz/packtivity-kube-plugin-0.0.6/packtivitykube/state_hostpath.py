def make_binds(state, stateopts):
    container_mounts = []
    volumes = []
    for i,path in enumerate(state.readwrite + state.readonly):
        volumes.append({
            "name": "packtivitystate{}".format(i),
            "hostPath": {
                "path": path
            }
        })

        container_mounts.append({
            "name": "packtivitystate{}".format(i),
            "mountPath": path
     })
    return container_mounts, volumes
