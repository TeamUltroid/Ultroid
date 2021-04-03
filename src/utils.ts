export const getDuration = (time: string | number): string => {
    if (typeof (time) === 'string') {
        time = parseInt(time)
    }
    let min = Math.floor(time / 60);
    let sec = time - min * 60;
    return `${min}m ${sec}s`;
}