def build_minimal_editor_state() -> dict[str, object]:
    return {
        "compositionWidth": 1920,
        "compositionHeight": 1080,
        "timebaseTicksPerSecond": 240000,
        "tracks": [
            {
                "id": "track-1",
                "items": ["item-solid-1"],
                "hidden": False,
                "muted": False,
            }
        ],
        "assets": {},
        "items": {
            "item-solid-1": {
                "id": "item-solid-1",
                "type": "solid",
                "startTicks": 0,
                "durationTicks": 120,
                "isDraggingInTimeline": False,
                "top": {"value": 0, "keyframes": []},
                "left": {"value": 0, "keyframes": []},
                "width": {"value": 320, "keyframes": []},
                "height": {"value": 180, "keyframes": []},
                "scaleX": {"value": 1, "keyframes": []},
                "scaleY": {"value": 1, "keyframes": []},
                "opacity": {"value": 1, "keyframes": []},
                "color": "#111827",
                "shape": "rectangle",
                "keepAspectRatio": False,
                "borderRadius": {"value": 0, "keyframes": []},
                "rotation": {"value": 0, "keyframes": []},
            }
        },
        "transitions": {},
    }
