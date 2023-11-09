export const useOnKeyPressed = (key: string, onAfterPressed: (event: globalThis.KeyboardEvent) => void): void => {
  const keyDown = useCallback(
    (event: globalThis.KeyboardEvent) => {
      if (event.key === key) {
        onAfterPressed(event);
      }
    },
    [onAfterPressed, key],
  );
  useEffect(() => {
    document.addEventListener("keydown", keyDown);
    return () => {
      document.removeEventListener("keydown", keyDown);
    };
  }, [keyDown]);
};
