import { useOnKeyPressed } from "./useOnKeyPressed";

// global keyboard shortcuts
export const KEYBOARD_SHORTCUTS = ["[", "/"] as const;
export type KeyboardShortcut = (typeof KEYBOARD_SHORTCUTS)[number];

/**
 * Add a new global key shortcut handler.
 */
export const useGlobalKeyShortcut = (
  key: KeyboardShortcut,
  onAfterPressed: (event: globalThis.KeyboardEvent) => void,
): void => {
  useOnKeyPressed(key, (event) => {
    // ignore keyboard events with modifiers
    if (event.ctrlKey || event.altKey || event.metaKey) {
      return;
    }
    // ignore keyboard events from input elements
    if ((event.target as Element).nodeName !== "INPUT") {
      onAfterPressed(event);
    }
  });
};
