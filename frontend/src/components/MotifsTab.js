import React, { useState, useEffect, useRef } from "react";
import {
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  TextField,
  CircularProgress,
  Button,
  MenuItem,
  Select,
  InputLabel,
  FormControl,
  Pagination,
  FormControlLabel,
  Switch,
  Modal,
  Typography,
} from "@mui/material";

export default function MotifsTab() {
  const [motifs, setMotifs] = useState([]);
  const [citations, setCitations] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [newMotifContent, setNewMotifContent] = useState("");
  const [selectedCitation, setSelectedCitation] = useState("");
  const [page, setPage] = useState(1);
  const [pageSize] = useState(10);
  const [totalMotifs, setTotalMotifs] = useState(0);
  const [deleteEnabled, setDeleteEnabled] = useState(false);
  const [showClozeDeletions, setShowClozeDeletions] = useState(true);
  const [hoveredClozeSet, setHoveredClozeSet] = useState({
    motifId: null,
    set: null,
  });
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalMotif, setModalMotif] = useState(null);
  const [newTuples, setNewTuples] = useState("");
  const [highlightedRanges, setHighlightedRanges] = useState([]);
  const [selectedBins, setSelectedBins] = useState(new Set());
  const [isDragging, setIsDragging] = useState(false);

  useEffect(() => {
    const fetchMotifs = () => {
      setIsLoading(true);
      fetch(`http://127.0.0.1:5000/motifs?page=${page}&page_size=${pageSize}`)
        .then((response) => response.json())
        .then((data) => {
          setMotifs(data.motifs || []);
          setTotalMotifs(data.total_count || 0);
          setIsLoading(false);
        })
        .catch((error) => {
          console.error("Error fetching motifs:", error);
          setMotifs([]);
          setTotalMotifs(0);
          setIsLoading(false);
        });
    };

    fetchMotifs();
    fetch("http://127.0.0.1:5000/citations")
      .then((response) => response.json())
      .then((data) => {
        setCitations(data || []);
      })
      .catch((error) => {
        console.error("Error fetching citations:", error);
        setCitations([]);
      });
  }, [page, pageSize]);

  const handleAddMotif = () => {
    if (!newMotifContent.trim()) return;
    fetch("http://127.0.0.1:5000/motifs", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        content: newMotifContent,
        citation: selectedCitation,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        const updatedMotifs = [data, ...motifs];
        setMotifs(updatedMotifs);
        setNewMotifContent("");
      })
      .catch((error) => {
        console.error("Error adding motif:", error);
      });
  };

  const handleSave = (uuid, content) => {
    fetch(`http://127.0.0.1:5000/motifs/${uuid}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ content }),
    })
      .then((response) => response.json())
      .catch((error) => {
        console.error("Error updating motif:", error);
      });
  };

  const handleDelete = (uuid) => {
    fetch(`http://127.0.0.1:5000/motifs/${uuid}`, {
      method: "DELETE",
    })
      .then(() => {
        setMotifs(motifs.filter((motif) => motif.uuid !== uuid));
      })
      .catch((error) => {
        console.error("Error deleting motif:", error);
      });
  };

  const handlePageChange = (event, value) => {
    setPage(value);
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter") {
      handleAddMotif();
    }
  };

  const handleMotifContentChange = (uuid, newContent) => {
    setMotifs(
      motifs.map((motif) =>
        motif.uuid === uuid ? { ...motif, content: newContent } : motif
      )
    );
  };

  const handleOpenModal = (
    motif,
    clozeDeletionSet,
    clozeDeletionUuid = null
  ) => {
    setModalMotif({ ...motif, clozeDeletionUuid });

    const initialBins = new Set(
      (clozeDeletionSet || []).flatMap(([start, end]) =>
        Array.from({ length: end - start + 1 }, (_, i) => start + i)
      )
    );

    setSelectedBins(initialBins);
    setIsModalOpen(true);
  };

  const renderClozeDeletions = (motifId, content, clozeDeletions) => {
    if (!clozeDeletions || clozeDeletions.length === 0) return "";

    return clozeDeletions
      .map(({ uuid, mask_tuples: set }, index) => (
        <span
          key={uuid || index} // Ensure a unique key
          onMouseEnter={() => setHoveredClozeSet({ motifId, set })}
          onMouseLeave={() => setHoveredClozeSet({ motifId: null, set: null })}
          onClick={() =>
            handleOpenModal(
              motifs.find((m) => m.uuid === motifId),
              set,
              uuid
            )
          }
          style={{
            cursor: "pointer",
            textDecoration: "underline",
            color: "gray",
          }}
        >
          cloze-deletion-{index + 1}
        </span>
      ))
      .reduce((prev, curr) => [prev, ", ", curr]);
  };

  const renderHighlightedContent = (motifId, content) => {
    if (!hoveredClozeSet.set || hoveredClozeSet.motifId !== motifId) {
      return content;
    }

    const highlightedIndexes = new Set(
      hoveredClozeSet.set.flatMap(([start, end]) =>
        Array.from({ length: end - start + 1 }, (_, i) => start + i)
      )
    );

    return content.split("").map((char, index) => (
      <span
        key={index}
        style={{
          backgroundColor: highlightedIndexes.has(index)
            ? "gray"
            : "transparent",
        }}
      >
        {char}
      </span>
    ));
  };

  const handleContentEditableInput = (e, motifId) => {
    const selection = window.getSelection();
    const range = selection.getRangeAt(0);
    const caretOffset = range.startOffset;

    const newContent = e.target.innerText;
    handleMotifContentChange(motifId, newContent);

    // Restore caret position
    window.requestAnimationFrame(() => {
      const newRange = document.createRange();
      newRange.setStart(
        e.target.firstChild,
        Math.min(caretOffset, newContent.length)
      );
      newRange.collapse(true);
      selection.removeAllRanges();
      selection.addRange(newRange);
    });
  };

  const handleContentEditableBlur = (e, motifId) => {
    const newContent = e.target.innerText;
    handleSave(motifId, newContent);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setModalMotif(null);
  };

  const handleSaveTuples = () => {
    const mask_tuples = [];
    let start = null;

    [...selectedBins]
      .sort((a, b) => a - b)
      .forEach((index, i, arr) => {
        if (start === null) start = index;
        if (i === arr.length - 1 || arr[i + 1] !== index + 1) {
          mask_tuples.push([start, index]);
          start = null;
        }
      });

    const payload = {
      mask_tuples,
      ...(modalMotif.clozeDeletionUuid
        ? { uuid: modalMotif.clozeDeletionUuid }
        : { motif_uuid: modalMotif.uuid }),
    };

    const method = modalMotif.clozeDeletionUuid ? "PUT" : "POST";

    fetch("http://127.0.0.1:5000/cloze_deletions", {
      method,
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log("Cloze deletion saved:", data);

        // Update the motif's cloze deletions list
        setMotifs((prevMotifs) =>
          prevMotifs.map((motif) =>
            motif.uuid === modalMotif.uuid
              ? {
                  ...motif,
                  cloze_deletions: modalMotif.clozeDeletionUuid
                    ? motif.cloze_deletions.map((cd) =>
                        cd.uuid === data.uuid ? data : cd
                      )
                    : [...(motif.cloze_deletions || []), data],
                }
              : motif
          )
        );
      })
      .catch((error) => {
        console.error("Error saving cloze deletion:", error);
      });

    handleCloseModal();
  };

  const handleDeleteClozeDeletion = () => {
    if (!modalMotif.clozeDeletionUuid) return;

    fetch(
      `http://127.0.0.1:5000/cloze_deletions/${modalMotif.clozeDeletionUuid}`,
      {
        method: "DELETE",
      }
    )
      .then((response) => response.json())
      .then(() => {
        console.log("Cloze deletion deleted");

        // Remove the cloze deletion from the motif's list
        setMotifs((prevMotifs) =>
          prevMotifs.map((motif) =>
            motif.uuid === modalMotif.uuid
              ? {
                  ...motif,
                  cloze_deletions: motif.cloze_deletions.filter(
                    (cd) => cd.uuid !== modalMotif.clozeDeletionUuid
                  ),
                }
              : motif
          )
        );
      })
      .catch((error) => {
        console.error("Error deleting cloze deletion:", error);
      });

    handleCloseModal();
  };

  const handleMouseDown = (index) => {
    setIsDragging(true);
    setSelectedBins(
      (prev) =>
        prev.has(index)
          ? new Set([...prev].filter((i) => i !== index)) // Deselect if already selected
          : new Set([...prev, index]) // Select if not already selected
    );
  };

  const handleMouseEnter = (index) => {
    if (isDragging) {
      setSelectedBins(
        (prev) =>
          prev.has(index)
            ? new Set([...prev].filter((i) => i !== index)) // Deselect if already selected
            : new Set([...prev, index]) // Select if not already selected
      );
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const renderBins = (content) => {
    return content.split("").map((char, index) => (
      <span
        key={index}
        onMouseDown={() => handleMouseDown(index)}
        onMouseEnter={() => handleMouseEnter(index)}
        onMouseUp={handleMouseUp}
        style={{
          display: "inline-block",
          padding: "2px 4px",
          margin: "1px",
          borderRadius: "4px",
          backgroundColor: selectedBins.has(index) ? "gray" : "transparent",
          cursor: "pointer",
          userSelect: "none",
        }}
      >
        {char}
      </span>
    ));
  };

  return (
    <Box>
      <Box mb={3}>
        <TextField
          fullWidth
          multiline
          minRows={3}
          label="New Motif Content"
          value={newMotifContent}
          onChange={(e) => setNewMotifContent(e.target.value)}
          onKeyDown={handleKeyDown}
          sx={{ mb: 2 }}
        />
        <FormControl fullWidth sx={{ mb: 2 }}>
          <InputLabel id="citation-select-label" shrink={true}>
            Citation
          </InputLabel>
          <Select
            labelId="citation-select-label"
            value={selectedCitation}
            onChange={(e) => setSelectedCitation(e.target.value)}
            displayEmpty
          >
            <MenuItem value="">
              <em>None</em>
            </MenuItem>
            {citations.map((citation) => (
              <MenuItem key={citation.uuid} value={citation.title}>
                {citation.title}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>
      {isLoading ? (
        <CircularProgress />
      ) : (
        <>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell sx={{ width: "50%" }}>Content</TableCell>
                  <TableCell sx={{ width: "20%" }}>Citation</TableCell>
                  <TableCell sx={{ width: "20%" }}>Created At</TableCell>
                  {deleteEnabled && (
                    <TableCell sx={{ width: "10%" }}>Actions</TableCell>
                  )}
                </TableRow>
              </TableHead>
              <TableBody>
                {motifs.map((motif) => (
                  <TableRow key={motif.uuid}>
                    <TableCell>
                      <div
                        contentEditable
                        suppressContentEditableWarning
                        style={{
                          borderRadius: "4px",
                          padding: "8px",
                          minHeight: "60px",
                          whiteSpace: "pre-wrap",
                          overflowWrap: "break-word",
                        }}
                        onInput={(e) =>
                          handleContentEditableInput(e, motif.uuid)
                        }
                        onBlur={(e) => handleContentEditableBlur(e, motif.uuid)}
                      >
                        {hoveredClozeSet.motifId === motif.uuid
                          ? renderHighlightedContent(motif.uuid, motif.content)
                          : motif.content}
                      </div>
                      {showClozeDeletions && (
                        <Box mt={1} display="flex" alignItems="center">
                          <Box>
                            {renderClozeDeletions(
                              motif.uuid,
                              motif.content,
                              motif.cloze_deletions
                            )}
                          </Box>
                          <Button
                            size="small"
                            onClick={() => handleOpenModal(motif, [])}
                            sx={{ ml: 2 }}
                          >
                            + add
                          </Button>
                        </Box>
                      )}
                    </TableCell>
                    <TableCell>{motif.citation}</TableCell>
                    <TableCell>
                      {new Date(motif.created_at).toLocaleString()}
                    </TableCell>
                    {deleteEnabled && (
                      <TableCell>
                        <Button
                          variant="contained"
                          color="secondary"
                          onClick={() => handleDelete(motif.uuid)}
                        >
                          Delete
                        </Button>
                      </TableCell>
                    )}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
          <Pagination
            count={Math.ceil(totalMotifs / pageSize)}
            page={page}
            onChange={handlePageChange}
            sx={{ mt: 2 }}
          />
        </>
      )}
      <Box mt={3}>
        <FormControlLabel
          control={
            <Switch
              checked={deleteEnabled}
              onChange={(e) => setDeleteEnabled(e.target.checked)}
              color="primary"
            />
          }
          label="Show delete buttons"
        />
      </Box>
      <Box mt={3}>
        <FormControlLabel
          control={
            <Switch
              checked={showClozeDeletions}
              onChange={() => setShowClozeDeletions((prev) => !prev)}
            />
          }
          label="Show cloze deletions"
          sx={{ mb: 2 }}
        />
      </Box>
      <Modal open={isModalOpen} onClose={handleCloseModal}>
        <Box
          sx={{
            position: "absolute",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -50%)",
            width: 400,
            bgcolor: "background.paper",
            boxShadow: 24,
            p: 4,
            borderRadius: 2,
          }}
          onMouseLeave={() => setIsDragging(false)} // Ensure dragging stops when leaving the modal
        >
          {modalMotif && (
            <Box
              mb={2}
              sx={{
                whiteSpace: "pre-wrap",
                wordWrap: "break-word",
                border: "1px solid #ccc",
                padding: "8px",
                borderRadius: "4px",
                cursor: "pointer",
              }}
              onMouseUp={handleMouseUp} // Ensure dragging stops when releasing the mouse
            >
              {renderBins(modalMotif.content)}
            </Box>
          )}
          <Typography variant="body2" mb={2}>
            Click and drag over the text to select or deselect sections for a
            cloze deletion set.
          </Typography>
          <Button
            variant="contained"
            color="primary"
            onClick={handleSaveTuples}
            sx={{ mr: 1 }}
          >
            Save
          </Button>
          {modalMotif?.clozeDeletionUuid && (
            <Button
              variant="contained"
              color="secondary"
              onClick={handleDeleteClozeDeletion}
              sx={{ mr: 1 }}
            >
              Delete
            </Button>
          )}
          <Button variant="outlined" onClick={handleCloseModal}>
            Cancel
          </Button>
        </Box>
      </Modal>
    </Box>
  );
}
