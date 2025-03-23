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
  const [showClozeDeletions, setShowClozeDeletions] = useState(false);
  const [hoveredClozeSet, setHoveredClozeSet] = useState({
    motifId: null,
    set: null,
  });

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

  const renderClozeDeletions = (motifId, content, clozeDeletions) => {
    if (!clozeDeletions || clozeDeletions.length === 0) return "None";

    return clozeDeletions
      .map((set, index) => (
        <span
          key={index}
          onMouseEnter={() => setHoveredClozeSet({ motifId, set })}
          onMouseLeave={() => setHoveredClozeSet({ motifId: null, set: null })}
          style={{ cursor: "pointer", textDecoration: "underline" }}
        >
          {set.map(([start, end]) => content.slice(start, end + 1)).join(", ")}
        </span>
      ))
      .reduce((prev, curr) => [prev, " | ", curr]);
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
            ? "yellow"
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
                  {showClozeDeletions && (
                    <TableCell sx={{ width: "10%" }}>Cloze Deletions</TableCell>
                  )}
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
                          border: "1px solid #ccc",
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
                    </TableCell>
                    <TableCell>{motif.citation}</TableCell>
                    <TableCell>
                      {new Date(motif.created_at).toLocaleString()}
                    </TableCell>
                    {showClozeDeletions && (
                      <TableCell>
                        {renderClozeDeletions(
                          motif.uuid,
                          motif.content,
                          motif.cloze_deletions
                        )}
                      </TableCell>
                    )}
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
    </Box>
  );
}
