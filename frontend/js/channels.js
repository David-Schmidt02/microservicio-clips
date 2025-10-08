/**
 * Mapeo de canales: slug -> información completa del canal
 * Este archivo mantiene la información de nombres de canales para mostrar
 * títulos legibles independientemente del contexto de la transcripción
 */

export const CHANNELS_MAP = {
  'olgaenvivo_': {
    name: 'Olga en Vivo',
    slug: 'olgaenvivo_'
  },
  'luzutv': {
    name: 'Luzu TV',
    slug: 'luzutv'
  },
  'todonoticias': {
    name: 'Todo Noticias',
    slug: 'todonoticias'
  },
  'neuramedia': {
    name: 'Neura Media',
    slug: 'neuramedia'
  },
  'lanacion': {
    name: 'La Nación',
    slug: 'lanacion'
  },
  'c5n': {
    name: 'C5N',
    slug: 'c5n'
  },
  'a24com': {
    name: 'A24',
    slug: 'a24com'
  },
  'telefenoticias': {
    name: 'Telefe Noticias',
    slug: 'telefenoticias'
  },
  'urbanaplayfm': {
    name: 'Urbana Play FM',
    slug: 'urbanaplayfm'
  }
};

/**
 * Obtiene el nombre legible de un canal a partir de su slug
 * @param {string} slug - El slug del canal (ej: 'todonoticias')
 * @returns {string} El nombre legible del canal (ej: 'Todo Noticias')
 */
export function getChannelName(slug) {
  if (!slug || typeof slug !== 'string') return 'Canal Desconocido';
  
  const channel = CHANNELS_MAP[slug.toLowerCase()];
  return channel ? channel.name : slug; // Fallback al slug si no está mapeado
}

/**
 * Obtiene información completa del canal
 * @param {string} slug - El slug del canal
 * @returns {Object} Información completa del canal
 */
export function getChannelInfo(slug) {
  if (!slug || typeof slug !== 'string') {
    return { name: 'Canal Desconocido', slug: 'unknown' };
  }
  
  const channel = CHANNELS_MAP[slug.toLowerCase()];
  return channel || { name: slug, slug: slug };
}