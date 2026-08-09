/** Keeps chart rendering responsive on 10k-step runs by capping the
 * number of points per series - same idea as core/reporting's sparklines. */
export function subsample<T>(values: T[], maxPoints = 500): T[] {
  if (values.length <= maxPoints) {
    return values;
  }
  const step = values.length / maxPoints;
  return Array.from({ length: maxPoints }, (_, i) => values[Math.floor(i * step)]);
}
