import React, { useState, useEffect } from "react";
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
  const [deleteEnabled, setDeleteEnabled] = useState(false); // State to control delete button visibility

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
        motif.uuid === uuid ? { ...motif, content: newContent } : motif,
      ),
    );
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
                      <TextField
                        fullWidth
                        multiline
                        minRows={3}
                        value={motif.content}
                        onChange={(e) =>
                          handleMotifContentChange(motif.uuid, e.target.value)
                        }
                        onBlur={() => handleSave(motif.uuid, motif.content)}
                      />
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
    </Box>
  );
}
