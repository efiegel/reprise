export const applyMasking = (content, maskTuples, mask) => {
  let maskedContent = content;
  let nRemovedCharacters = 0;

  maskTuples.forEach(([start, end]) => {
    start -= nRemovedCharacters;
    end -= nRemovedCharacters;

    maskedContent =
      maskedContent.slice(0, start) + mask + maskedContent.slice(end + 1);
    nRemovedCharacters += end - start + 1 - mask.length;
  });

  return maskedContent;
};
