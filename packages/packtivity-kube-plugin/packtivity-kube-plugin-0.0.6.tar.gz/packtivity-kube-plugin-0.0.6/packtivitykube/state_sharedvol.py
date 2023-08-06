import os
def make_binds(state, stateopts):
    container_mounts = []
    volumes = []
    shared_mount = stateopts['shared_mount']
    for i,path in enumerate(state.readwrite + state.readonly):
        container_mounts.append({
            "name": "packtivitystate",
            "mountPath": path,
            "subPath": os.path.relpath(path,shared_mount)
        })

    volumes.append({
        "name": "packtivitystate",
    })
    volumes[0].update(**stateopts['shared_volume'])
    return container_mounts, volumes
