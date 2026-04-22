"""Convert iCalendar (ICS) components to flatdir JSON entries."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class IcsProperty:
    name: str
    value: str
    parameters: dict[str, str | list[str]] = field(default_factory=dict)


@dataclass
class IcsComponent:
    name: str
    properties: list[IcsProperty] = field(default_factory=list)
    components: list["IcsComponent"] = field(default_factory=list)


def list_ics_entries(path: Path, component: str = "VEVENT") -> list[dict[str, object]]:
    calendar = parse_ics(path.read_text(encoding="utf-8-sig", errors="replace"))
    wanted = component.upper()
    components = [
        item
        for item in _walk_components(calendar)
        if item.name != "VCALENDAR" and (wanted == "ALL" or item.name == wanted)
    ]
    return [_component_to_entry(item) for item in components]


def parse_ics(text: str) -> IcsComponent:
    stack: list[IcsComponent] = []
    root: IcsComponent | None = None

    for line in _unfold_lines(text.splitlines()):
        if not line:
            continue

        prop = _parse_property(line)
        if prop.name == "BEGIN":
            component = IcsComponent(prop.value.upper())
            if stack:
                stack[-1].components.append(component)
            else:
                root = component
            stack.append(component)
            continue

        if prop.name == "END":
            if not stack:
                raise ValueError(f"END:{prop.value} without matching BEGIN")
            ended = stack.pop()
            if ended.name != prop.value.upper():
                raise ValueError(f"END:{prop.value} does not match BEGIN:{ended.name}")
            continue

        if not stack:
            continue
        stack[-1].properties.append(prop)

    if stack:
        raise ValueError(f"missing END:{stack[-1].name}")
    if root is None:
        raise ValueError("ICS data does not contain a component")
    return root


def _component_to_entry(component: IcsComponent) -> dict[str, object]:
    entry: dict[str, object] = {"BEGIN": component.name}

    for prop in component.properties:
        _add_value(entry, prop.name, _property_json_value(prop))

    for child in component.components:
        _add_value(entry, child.name, _component_to_entry(child))

    entry["END"] = component.name
    return entry


def _property_json_value(prop: IcsProperty) -> str | dict[str, object]:
    if not prop.parameters:
        return prop.value
    return {
        "value": prop.value,
        "parameters": prop.parameters,
    }


def _add_value(entry: dict[str, object], key: str, value: object) -> None:
    if key not in entry:
        entry[key] = value
        return

    existing = entry[key]
    if isinstance(existing, list):
        existing.append(value)
    else:
        entry[key] = [existing, value]


def _walk_components(component: IcsComponent) -> list[IcsComponent]:
    components = [component]
    for child in component.components:
        components.extend(_walk_components(child))
    return components


def _unfold_lines(lines: list[str]) -> list[str]:
    unfolded: list[str] = []
    for line in lines:
        if line.startswith((" ", "	")) and unfolded:
            unfolded[-1] += line[1:]
        else:
            unfolded.append(line)
    return unfolded


def _parse_property(line: str) -> IcsProperty:
    name_and_params, separator, value = line.partition(":")
    if separator == "":
        return IcsProperty(name=line.upper(), value="")

    parts = name_and_params.split(";")
    name = parts[0].upper()
    parameters: dict[str, str | list[str]] = {}
    for param in parts[1:]:
        key, has_value, param_value = param.partition("=")
        key = key.upper()
        if not has_value:
            parameters[key] = ""
        elif "," in param_value:
            parameters[key] = [item.strip() for item in param_value.split(",")]
        else:
            parameters[key] = param_value

    return IcsProperty(name=name, value=value, parameters=parameters)
