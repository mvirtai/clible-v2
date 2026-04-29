// Re-export the shared pool so route files that previously imported `usersDb`
// from this module can be updated to import `pool` from here.
export { pool } from '../db/pool.js';
