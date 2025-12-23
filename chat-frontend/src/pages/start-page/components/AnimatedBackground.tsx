import { PropsWithChildren, useEffect, useRef } from "react"

interface Point {
    x: number;
    y: number;
};

interface AnimatedBackgroundProps extends PropsWithChildren {
    color?: string;
    durationMs?: number;
    className?: string;
}

type SvgTriangle = {
  points: string; // "x1,y1 x2,y2 x3,y3"
};

export default function AnimatedBackground({
    children,
    color = "#3b82f6",
    durationMs = 5000,
    className = ""}: AnimatedBackgroundProps) {
    const polygonRef = useRef<SVGLineElement | null>(null);
    const currentRef = useRef<Point[]>([]);

    const POINTS = 400;
    const WIDTH = 1000;
    const HEIGHT = 400;

    function generateRandomPoints() {
        return Array.from({ length: POINTS }, () => ({
            x: Math.random() * WIDTH,
            y: Math.random() * HEIGHT,
        }));
    }

    function twoNearestPoints(
        target: Point,
        points: Point[]
        ): [Point, Point] | null {
        let nearest1: Point | null = null;
        let nearest2: Point | null = null;

        let d1 = Infinity;
        let d2 = Infinity;

        for (const p of points) {
            // exclude self (same reference OR same coordinates)
            if (p === target || (p.x === target.x && p.y === target.y)) {
            continue;
            }

            const distSq =
            (p.x - target.x) ** 2 +
            (p.y - target.y) ** 2;

            if (distSq < d1) {
            // shift first → second
            d2 = d1;
            nearest2 = nearest1;

            d1 = distSq;
            nearest1 = p;
            } else if (distSq < d2) {
            d2 = distSq;
            nearest2 = p;
            }
        }

        return nearest1 && nearest2 ? [nearest1, nearest2] : null;
    }

    function createSvgTriangles(points: Point[]): SvgTriangle[] {
        const triangles: SvgTriangle[] = [];
        const seen = new Set<string>();

        for (const p of points) {
            const nearest = twoNearestPoints(p, points);
            if (!nearest) continue;

            const tri = [p, nearest[0], nearest[1]];

            // dedupe by sorted coordinate key
            const key = tri
            .map(pt => `${pt.x},${pt.y}`)
            .sort()
            .join("|");

            if (seen.has(key)) continue;
            seen.add(key);

            triangles.push({
            points: tri.map(pt => `${pt.x},${pt.y}`).join(" "),
            });
        }

        return triangles;
    }

    function generateTriangleMesh(points: Point[]): SvgTriangle[] {
        const triangles: SvgTriangle[] = [];
        const seen = new Set<string>();

        for (const p of points) {
            const nearest = twoNearestPoints(p, points);
            if (!nearest) continue;

            const tri = [p, nearest[0], nearest[1]];

            // prevent duplicate triangles
            const key = tri
            .map(pt => `${pt.x},${pt.y}`)
            .sort()
            .join("|");

            if (seen.has(key)) continue;
            seen.add(key);

            triangles.push({
            points: tri.map(pt => `${pt.x},${pt.y}`).join(" "),
            });
        }

        return triangles;
    }

    function pointsToString(points: Point[]) {
        return points.map(p => `${p.x},${p.y}`).join(" ");
    }

    // useEffect(() => {
    //     if (!polygonRef.current) {
    //         return;
    //     }

    //     let rafID: number;
    //     let startTime = 0;

    //     // currentRef.current = randomStrip();
    //     polygonRef.current.setAttribute("points", pointsToString(currentRef.current));

    //     // function morph() {
    //     //     const next = randomStrip();
    //     //     startTime = performance.now();

    //     //     function animate(t: number) {
    //     //         const progress = Math.min((t - startTime / durationMs), 1);
    //     //         const eased = progress * progress * (3 - 2 * progress);
    //     //         const interpolated = currentRef.current.map((pt, i) => ({
    //     //             x: pt.x + (next[i].x - pt.x) * eased,
    //     //             y: pt.y + (next[i].y - pt.y) * eased,
    //     //         }));

    //     //         polygonRef.current!.setAttribute("points", pointsToString(interpolated));

    //     //         if (progress < 1) {
    //     //             rafID = requestAnimationFrame(animate);
    //     //         } else {
    //     //             currentRef.current = next;
    //     //             rafID = requestAnimationFrame(morph);
    //     //         }
    //     //     }

    //     //     rafID = requestAnimationFrame(animate);
    //     // }

    //     // morph();

    //     // return () => cancelAnimationFrame(rafID);
    // },
    // [durationMs]);

    return <div className={className}>
        <svg
            viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
            preserveAspectRatio="none"
            style={{width: "100%", height: "100%"}}
            aria-hidden>
            {generateTriangleMesh(generateRandomPoints()).map((t, i) =>
                <polygon
                    key={i}
                    points={t.points}
                    fill="none"
                    stroke="white"
                    strokeWidth="1"
                    />)}
        </svg>
        {children}
    </div>
}