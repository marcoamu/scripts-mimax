/**
 * Book Library - Track books you've read
 */

const fs = require('fs');

const BOOKS_FILE = '/root/.openclaw/workspace/data/books.json';

// Default books
const DEFAULT_BOOKS = [
  { id: 1, title: 'Atomic Habits', author: 'James Clear', status: 'reading', rating: 0, notes: '' },
  { id: 2, title: 'Deep Work', author: 'Cal Newport', status: 'read', rating: 5, notes: '' },
  { id: 3, title: 'The Pragmatic Programmer', author: 'David Thomas', status: 'want_to_read', rating: 0, notes: '' }
];

// Initialize books file
function initBooks() {
  if (!fs.existsSync(BOOKS_FILE)) {
    fs.writeFileSync(BOOKS_FILE, JSON.stringify(DEFAULT_BOOKS, null, 2));
  }
}

// Get all books
function getBooks() {
  initBooks();
  return JSON.parse(fs.readFileSync(BOOKS_FILE, 'utf8'));
}

// Add a book
function addBook(book) {
  initBooks();
  const books = JSON.parse(fs.readFileSync(BOOKS_FILE, 'utf8'));
  
  const newBook = {
    id: Date.now(),
    title: book.title,
    author: book.author || 'Unknown',
    status: book.status || 'want_to_read',
    rating: 0,
    notes: '',
    addedAt: new Date().toISOString()
  };
  
  books.push(newBook);
  fs.writeFileSync(BOOKS_FILE, JSON.stringify(books, null, 2));
  return newBook;
}

// Update book
function updateBook(id, updates) {
  initBooks();
  const books = JSON.parse(fs.readFileSync(BOOKS_FILE, 'utf8'));
  
  const index = books.findIndex(b => b.id === parseInt(id));
  if (index >= 0) {
    books[index] = { ...books[index], ...updates };
    fs.writeFileSync(BOOKS_FILE, JSON.stringify(books, null, 2));
    return books[index];
  }
  return null;
}

// Delete book
function deleteBook(id) {
  initBooks();
  let books = JSON.parse(fs.readFileSync(BOOKS_FILE, 'utf8'));
  books = books.filter(b => b.id !== parseInt(id));
  fs.writeFileSync(BOOKS_FILE, JSON.stringify(books, null, 2));
  return true;
}

// Get stats
function getStats() {
  const books = getBooks();
  
  return {
    total: books.length,
    read: books.filter(b => b.status === 'read').length,
    reading: books.filter(b => b.status === 'reading').length,
    wantToRead: books.filter(b => b.status === 'want_to_read').length,
    avgRating: books.filter(b => b.rating > 0).reduce((sum, b, _, arr) => sum + b.rating / arr.length, 0)
  };
}

module.exports = {
  getBooks,
  addBook,
  updateBook,
  deleteBook,
  getStats
};
